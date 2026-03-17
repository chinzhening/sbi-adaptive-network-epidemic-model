import json

import numpy as np

from src.abctools import run_abc_rejection

from src.abctools.config import ABCConfig
from src.abctools.diagnostics import generate_diagnostics
from src.abctools.distance import *
from src.abctools.normalization import *
from src.abctools.summary import *

from src.simulator import simulate_ensemble

from src.utils import load_observed_data
from src.utils import save_result, save_fig, create_results_dir, log_experiment

# --- CONFIG ---
def simulate(params: dict) -> tuple:
    beta, gamma, rho = params["beta"], params["gamma"], params["rho"]
    n_replicates = 40
    return simulate_ensemble(beta, gamma, rho, n_replicates)

def prior() -> dict:
    return {
        "beta": np.random.uniform(0.05, 0.50),
        "gamma": np.random.uniform(0.02, 0.20),
        "rho": np.random.uniform(0.0, 0.8),
    }


# --- MAIN EXPERIMENT ---
def main():
    obs_data = load_observed_data()
    
    config = ABCConfig(
        simulate=simulate,
        prior=prior,
        summary_stats=[
            mean_auc_infected,
            mean_initial_slope_infected,
            mean_total_rewire,
            mean_cumulative_infected_fraction_until_first_rewire,
        ],
        normalization=median_absolute_deviation,
        distance=euclidean,
        epsilon=0.5,
        n_simulations=100_000,
        param_names=("beta", "gamma", "rho"),
        observed_data=obs_data,
    )

    result = run_abc_rejection(config)

    # generate diagnostics plots and posterior stats
    diagnostic_plots, posterior_stats = generate_diagnostics(result)

    # save results
    experiment_name = __file__.split("\\")[-1].split(".")[0]  # get filename without extension
    results_dir = create_results_dir(experiment_name)
    save_result(result, results_dir)

    for name, fig in diagnostic_plots.items():
        save_fig(fig, results_dir, f"{name}.png")

    # Logging
    print(f"Experiment '{experiment_name}' completed.")
    print(f"Results saved to '{results_dir}'")
    print(f"Total runtime: {result.runtime_seconds:.2f}s")
    print(f"Avg runtime per simulation: {result.runtime_seconds / result.n_simulations:.4f}s")
    print(f"Acceptance Rate: {result.acceptance_rate * 100:.2f}%")

    log_experiment(config, result, results_dir)

    
    # dump posterior stats into a json file
    with open(f"{results_dir}/posterior_stats.json", "w") as f:
        json.dump(posterior_stats, f, indent=2)


if __name__ == "__main__":
    main()