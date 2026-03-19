import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from simulator import simulate_ensemble
from abctools.summary import *
from abctools.normalization import *
from abctools.distance import *


def visualise_summary_statistic(params1: dict, params2: dict, n_simulations: int = 100, n_replicates: int = 40) -> None:
    """Visualise the distribution of a summary statistic for two different sets of parameters."""
    beta1, gamma1, rho1 = params1["beta"], params1["gamma"], params1["rho"]
    beta2, gamma2, rho2 = params2["beta"], params2["gamma"], params2["rho"]
    
    stats1 = np.empty(shape=(n_simulations,))
    stats2 = np.empty(shape=(n_simulations,))

    summarize = lambda sim_data: mean_cumulative_infected_fraction_until_first_rewire(sim_data)

    for i in range(n_simulations):
        # simulate data for first set of params
        sim_data1 = simulate_ensemble(beta1, gamma1, rho1, n_replicates)
        stat1 = summarize(sim_data1)
        stats1[i] = stat1

        # simulate data for second set of params
        sim_data2 = simulate_ensemble(beta2, gamma2, rho2, n_replicates)
        stat2 = summarize(sim_data2)
        stats2[i] = stat2
    
    # equalize variance
    stats = np.concatenate([stats1, stats2])
    scale = equalize_variance(stats)
    stats1 = scale(stats1)
    stats2 = scale(stats2)


    # visualise the distribution of summary statistics
    sns.kdeplot(stats1, label=f"β={beta1:.2f}, γ={gamma1:.2f}, ρ={rho1:.2f}")
    sns.kdeplot(stats2, label=f"β={beta2:.2f}, γ={gamma2:.2f}, ρ={rho2:.2f}")
    plt.legend()
    plt.xlabel("Summary statistic")
    plt.title("Distribution of summary statistic for two sets of parameters")
    plt.show()

def plot_summary_statistics():
    # read results.csv
    data = np.genfromtxt("results.csv", delimiter=",", skip_header=1)
    normalize = equalize_variance(data)
    normalized_data = normalize(data)
    # plot the normalized summary statistics
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))
    stat_names = ["total_rewire", "sum_infected_until_first_rewire", "sd_degree"]
    for i in range(3):
        sns.kdeplot(normalized_data[:, i], ax=ax[i])
        ax[i].set_title(f"KDE of normalized {stat_names[i]}")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":

    visualise_summary_statistic(
        params1={"beta": 0.1, "gamma": 0.08, "rho": 0.05},
        params2={"beta": 0.1, "gamma": 0.08, "rho": 0.4},
        n_simulations=100,
        n_replicates=40,
    )
    # plot_summary_statistics()