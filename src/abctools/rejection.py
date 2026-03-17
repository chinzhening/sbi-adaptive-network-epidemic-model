import time

from .config import *

def _simulate_proposal(params: dict, config: ABCConfig) -> tuple:
    """
    Simulate data and compute summary statistics

    Parameters
    ----------
    params : dict
        Parameter vector in the order of config.param_names
    config : ABCConfig
        ABC configuration
    
    Returns
    -------
    s_sim : np.ndarray
        Simulated summary statistics
    """

    sim_data = config.simulate(params)
    s_sim = config.summarize(sim_data)

    return s_sim

def run_abc_rejection(config: ABCConfig) -> ABCResult:
    """
    Run ABC rejection sampling.

    Parameters
    ----------
    config : ABCConfig
        ABC configuration

    Returns
    -------
    ABCResult
    """

    start = time.perf_counter()

    n_params = len(config.param_names)

    n_simulations = config.n_simulations

    # compute observed summary statistics once
    s_obs = config.summarize(config.observed_data)
    n_stats = s_obs.shape[0]

    # allocate arrays
    proposed_params = np.empty((n_simulations, n_params))
    simulated_stats = np.empty((n_simulations, n_stats))
    distances = np.empty(n_simulations)
    accepted_mask = np.zeros(n_simulations, dtype=bool)

    # main sampling loop
    for i in range(n_simulations):

        # sample parameters from prior
        params = config.prior()
        s_sim = _simulate_proposal(params, config)

        # store
        proposed_params[i] = [params[p] for p in config.param_names]
        simulated_stats[i] = s_sim

        if (i + 1) % (n_simulations // 10) == 0:
            print(f"Processed {i+1}/{n_simulations} proposals.")

    # normalize summary statistics if normalization function is provided
    normalize = config.normalization(simulated_stats)
    simulated_stats = normalize(simulated_stats)
    s_obs = normalize(s_obs)

    # evaluate distances and acceptance
    for i in range(n_simulations):
        distances[i] = config.distance(s_obs, simulated_stats[i])

    accepted_mask = distances <= config.epsilon

    n_accepted = accepted_mask.sum()

    # accepted subsets
    accepted_params = proposed_params[accepted_mask]
    accepted_stats = simulated_stats[accepted_mask]

    acceptance_rate = accepted_mask.mean()

    print(f"Accepted {n_accepted} out of {n_simulations} proposals.")

    runtime = time.perf_counter() - start

    return ABCResult(
        proposed_params=proposed_params,
        accepted_params=accepted_params,
        simulated_stats=simulated_stats,
        accepted_stats=accepted_stats,
        observed_stats=s_obs,
        distances=distances,
        accepted_mask=accepted_mask,
        acceptance_rate=acceptance_rate,
        epsilon=config.epsilon,
        n_simulations=n_simulations,
        param_names=config.param_names,
        runtime_seconds=runtime,
    )