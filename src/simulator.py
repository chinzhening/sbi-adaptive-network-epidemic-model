"""
Adaptive-network SIR epidemic simulator.

This module simulates an SIR (Susceptible-Infected-Recovered) epidemic
spreading on a network that evolves over time. The key idea is that
susceptible individuals can "rewire" their connections to avoid infected
neighbors, which couples the disease dynamics with the network topology.

The model proceeds in discrete time steps, each with three phases:
  1. Infection: infected nodes transmit the disease to susceptible neighbors
  2. Recovery: infected nodes recover (and become immune)
  3. Rewiring: susceptible nodes break links with infected neighbors and
     form new connections elsewhere

Reference: Gross et al. (2006), "Epidemic dynamics on an adaptive network",
Physical Review Letters, 96(20), 208701.
"""

import numpy as np
import numba

from numba import prange


# ---------------------------------------------------------------------------
# Numba-compiled core
# ---------------------------------------------------------------------------
 
@numba.njit
def _simulate_one(adj, state, beta, gamma, rho, N, T):
    """Run a single replicate.  adj and state are modified in-place.
 
    Returns
    -------
    infected_fraction : float64 (T+1,)
    rewire_counts     : int64   (T+1,)
    """
    infected_fraction = np.zeros(T + 1, dtype=np.float64)
    rewire_counts     = np.zeros(T + 1, dtype=np.int64)
 
    cnt = np.int64(0)
    for i in range(N):
        if state[i] == 1:
            cnt += 1
    infected_fraction[0] = cnt / N
 
    # Private work buffers — allocated once per replicate, reused across steps
    max_edges   = N * N
    new_inf_buf = np.empty(N * N,     dtype=np.int64)
    si_s_buf    = np.empty(max_edges, dtype=np.int64)
    si_i_buf    = np.empty(max_edges, dtype=np.int64)
    cand_buf    = np.empty(N,         dtype=np.int64)
 
    for t in range(1, T + 1):
 
        # --- Phase 1: Infection (synchronous) ---
        n_new = np.int64(0)
        for i in range(N):
            if state[i] == 1:
                for j in range(N):
                    if adj[i, j] and state[j] == 0:
                        if np.random.random() < beta:
                            new_inf_buf[n_new] = j
                            n_new += 1
        for k in range(n_new):
            state[new_inf_buf[k]] = 1
 
        # --- Phase 2: Recovery ---
        for i in range(N):
            if state[i] == 1:
                if np.random.random() < gamma:
                    state[i] = 2
 
        # --- Phase 3: Rewiring ---
        n_si = np.int64(0)
        for i in range(N):
            if state[i] == 0:
                for j in range(N):
                    if adj[i, j] and state[j] == 1:
                        si_s_buf[n_si] = i
                        si_i_buf[n_si] = j
                        n_si += 1
 
        rewire_count = np.int64(0)
        for e in range(n_si):
            s_node = si_s_buf[e]
            i_node = si_i_buf[e]
            if np.random.random() >= rho:
                continue
            if not adj[s_node, i_node]:
                continue
            adj[s_node, i_node] = False
            adj[i_node, s_node] = False
            n_cand = np.int64(0)
            for k in range(N):
                if k != s_node and not adj[s_node, k]:
                    cand_buf[n_cand] = k
                    n_cand += 1
            if n_cand > 0:
                idx         = int(np.random.random() * n_cand)
                new_partner = cand_buf[idx]
                adj[s_node, new_partner] = True
                adj[new_partner, s_node] = True
                rewire_count += 1
 
        cnt = np.int64(0)
        for i in range(N):
            if state[i] == 1:
                cnt += 1
        infected_fraction[t] = cnt / N
        rewire_counts[t]     = rewire_count
 
    return infected_fraction, rewire_counts
 
 
# ---------------------------------------------------------------------------
# Parallel ensemble runner
# ---------------------------------------------------------------------------
 
@numba.njit(parallel=True)
def _run_ensemble(
    seeds,          # (R,) int64  — unique RNG seed per replicate
    beta, gamma, rho,
    N, p_edge, n_infected0, T,
    # Pre-allocated output arrays (written to by index, no race conditions)
    out_inf_frac,   # (R, T+1) float64
    out_rewires,    # (R, T+1) int64
    out_deg_hist,   # (R, 31)  int64
):
    R = seeds.shape[0]
 
    for r in prange(R):                 # <-- parallel loop over replicates
        # -----------------------------------------------------------------
        # Each iteration of prange runs in its own thread.  Everything
        # allocated inside the loop is private to that thread.
        # -----------------------------------------------------------------
 
        # Seed this thread's RNG independently
        np.random.seed(seeds[r])
 
        # Build a fresh Erdos-Renyi adjacency matrix for this replicate
        adj = np.zeros((N, N), dtype=numba.boolean)
        for i in range(N):
            for j in range(i + 1, N):
                if np.random.random() < p_edge:
                    adj[i, j] = True
                    adj[j, i] = True
 
        # Initialise node states
        state = np.zeros(N, dtype=numba.int8)
        # Fisher-Yates partial shuffle to pick n_infected0 unique nodes
        perm = np.arange(N, dtype=np.int64)
        for k in range(n_infected0):
            idx       = k + int(np.random.random() * (N - k))
            perm[k], perm[idx] = perm[idx], perm[k]
            state[perm[k]] = 1
 
        # Run the simulation
        inf_frac, rewires = _simulate_one(adj, state, beta, gamma, rho, N, T)
 
        # Write results into pre-allocated output slices (disjoint → no races)
        for t in range(T + 1):
            out_inf_frac[r, t] = inf_frac[t]
            out_rewires[r, t]  = rewires[t]
 
        # Degree histogram from final adjacency matrix
        for i in range(N):
            deg = np.int64(0)
            for j in range(N):
                if adj[i, j]:
                    deg += 1
            deg = min(deg, np.int64(30))
            out_deg_hist[r, deg] += 1
 
 
# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
 
def simulate_ensemble(
    beta, gamma, rho,
    n_replicates=64,
    N=200, p_edge=0.05, n_infected0=5, T=200,
    rng_seed=None,
):
    """Run ``n_replicates`` independent SIR simulations in parallel.
 
    Parameters
    ----------
    beta, gamma, rho : float
        Transmission, recovery, and rewiring probabilities (see simulate()).
    n_replicates : int, default=64
        Number of independent replicates to run.  More replicates → better
        estimates of ensemble statistics; they all run in parallel.
    N, p_edge, n_infected0, T : same as simulate()
    rng_seed : int or None
        Master seed.  Replicate seeds are derived deterministically from it,
        so the entire ensemble is reproducible.
 
    Returns
    -------
    infected_fraction : np.ndarray, shape (n_replicates, T+1)
        Fraction infected at each time step for every replicate.
    rewire_counts : np.ndarray, shape (n_replicates, T+1)
        Rewiring events per time step for every replicate.
    degree_histograms : np.ndarray, shape (n_replicates, 31)
        Final-step degree histogram for every replicate.
        Column d counts nodes with degree d (d=30 means degree ≥ 30).
 
    Notes
    -----
    The first call incurs a one-time Numba JIT compilation cost (~5-15 s).
    Subsequent calls with the same argument types are fast.
 
    The number of threads used equals ``numba.get_num_threads()``, which
    defaults to the number of logical CPU cores.  Override with
    ``numba.set_num_threads(n)`` before calling.
    """
    R = n_replicates
 
    # Derive per-replicate seeds from the master seed so results are
    # reproducible while each replicate still gets an independent RNG stream.
    master_rng = np.random.default_rng(rng_seed)
    seeds = master_rng.integers(0, 2**31, size=R, dtype=np.int64)
 
    # Pre-allocate output arrays (parallel writes go to disjoint rows)
    out_inf_frac  = np.zeros((R, T + 1), dtype=np.float64)
    out_rewires   = np.zeros((R, T + 1), dtype=np.int64)
    out_deg_hist  = np.zeros((R, 31),    dtype=np.int64)
 
    _run_ensemble(
        seeds, beta, gamma, rho,
        np.int64(N), p_edge, np.int64(n_infected0), np.int64(T),
        out_inf_frac, out_rewires, out_deg_hist,
    )
 
    return out_inf_frac, out_rewires, out_deg_hist
 
 
# ---------------------------------------------------------------------------
# Convenience: single-replicate wrapper (matches original simulate() API)
# ---------------------------------------------------------------------------
 
def simulate(beta, gamma, rho, N=200, p_edge=0.05, n_infected0=5, T=200, rng_seed=None):
    """Run one replicate of the adaptive-network SIR model.
 
    Parameters and return values are identical to the original implementation.
    The heavy inner loop is compiled by Numba for a large speed-up.
 
    Parameters
    ----------
    beta : float in [0, 1]
        Transmission probability per S-I edge per time step.
    gamma : float in [0, 1]
        Recovery probability per infected node per time step.
    rho : float in [0, 1]
        Rewiring probability per S-I edge per time step.
    N : int, default=200
        Number of nodes.
    p_edge : float, default=0.05
        Edge probability for the initial Erdos-Renyi graph.
    n_infected0 : int, default=5
        Number of initially infected nodes.
    T : int, default=200
        Number of time steps to simulate.
    rng_seed : int or None
        Seed for numpy's global RNG (for reproducibility).
 
    Returns
    -------
    infected_fraction : np.ndarray, shape (T+1,)
    rewire_counts     : np.ndarray, shape (T+1,)
    degree_histogram  : np.ndarray, shape (31,)
    """
    inf_frac, rewires, deg_hists = simulate_ensemble(
        beta, gamma, rho,
        n_replicates=1,
        N=N, p_edge=p_edge, n_infected0=n_infected0, T=T,
        rng_seed=rng_seed,
    )
    return inf_frac[0], rewires[0], deg_hists[0]