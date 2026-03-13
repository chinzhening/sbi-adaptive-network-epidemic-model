from os import times

if __name__ == "__main__":
    import time
    import numpy as np

    from simulator import simulate_ensemble

    # Example parameters
    beta, gamma, rho = 0.3, 0.1, 0.05
    N, p_edge, n_infected0 = 200, 0.05, 5
    T = 200

    # --- Warm up JIT (first call compiles, don't include in timing) ---
    simulate_ensemble(beta, gamma, rho, n_replicates=1, N=N, p_edge=p_edge,
                    n_infected0=n_infected0, T=T)
    print("JIT warm-up done.")


    n_replicates = 16 # number of ensemble replicates
    n_samples = 100_000  # number of total samples
    ensemble_runs = n_samples // n_replicates + 1  # number of times to run the ensemble to get n_samples total

    # Run the simulation to profile performance
    runtimes = np.empty(ensemble_runs)
    for i in range(ensemble_runs):
        t0 = time.perf_counter()
        simulate_ensemble(beta, gamma, rho, n_replicates=n_replicates,
                        N=N, p_edge=p_edge, n_infected0=n_infected0, T=T)
        runtimes[i] = time.perf_counter() - t0

    print(f"Ensemble size          : {n_replicates} replicates")
    print(f"Total samples          : {n_samples} samples")
    print(f"Number of runs         : {ensemble_runs} runs")
    print(f"Average runtime        : {runtimes.mean():.4f} seconds")
    print(f"Runtime std dev        : {runtimes.std():.4f} seconds")
    print(f"Total runtime          : {runtimes.sum():.4f} seconds")
    print(f"Average time per sample: {runtimes.sum() / n_samples:.4f} seconds")