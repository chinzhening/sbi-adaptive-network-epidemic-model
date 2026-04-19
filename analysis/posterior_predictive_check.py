import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from .simulate import simulate_summary_stats


# ----------------------------
# CONFIG
# ----------------------------
NPY_PATH = "results/preliminary/base_posterior_samples.npy"
DATA_DIR = Path("results/preliminary")
OUTPUT_DIR = Path("paper/figures/preliminary")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

SUMMARY_NAMES = [
    "auc_infected_fraction",
    "peak_infected_fraction",
    "initial_growth_ratio",
    "total_rewire_count",
    "sd_degree",
]

PARAM_NAMES = ["beta", "gamma", "rho"]

# ----------------------------
# LOAD POSTERIOR SAMPLES
# ----------------------------
posterior_samples = np.load(NPY_PATH)

accepted_params = [
    {
        PARAM_NAMES[i]: posterior_samples[j, i] for i in range(len(PARAM_NAMES))
    } for j in range(posterior_samples.shape[0])
]


# ----------------------------
# RUN POSTERIOR PREDICTIVE SIMULATION
# ----------------------------
ppc_df = simulate_summary_stats(
    params_list=accepted_params,
    stat_names=SUMMARY_NAMES,
    n_sim=1,
)

ppc_df.to_csv(f"{DATA_DIR}/posterior_predictive_samples.csv", index=False)


# ----------------------------
# LOAD OBSERVED SUMMARY STATS
# (assumes single row file or dict-like CSV)
# ----------------------------
obs = pd.read_csv("data/raw/observed_stats_raw.csv")

if len(obs) > 1:
    raise ValueError("Expected single-row observed summary stats file.")

obs = obs.iloc[0]


# ----------------------------
# PLOT PPC
# ----------------------------

n_stats = len(SUMMARY_NAMES)
fig, axes = plt.subplots(1, n_stats, figsize=(4 * n_stats, 3.5))

if n_stats == 1:
    axes = [axes]

for ax, stat in zip(axes, SUMMARY_NAMES):
    stat_name = "mean:" + stat

    sim_values = ppc_df[stat_name].values
    obs_value = obs[stat_name]

    ax.hist(sim_values, alpha=0.6, color="black")
    ax.axvline(obs_value, color="red", linewidth=2)

    ax.set_title(stat_name, fontsize=10)
    ax.tick_params(axis="x", rotation=45)

# shared legend (cleaner than repeating)
fig.legend(
    ["posterior predictive", "observed"],
    loc="upper center",
    ncol=2
)

fig.tight_layout(rect=[0, 0, 1, 0.9])

filename = "posterior_predictive_check"
plt.savefig(f"{OUTPUT_DIR}/{filename}.png", dpi=300)
plt.savefig(f"{DATA_DIR}/{filename}.png", dpi=300)
plt.close()

print("PPC completed. Saved:", f"{OUTPUT_DIR}/{filename}.png")