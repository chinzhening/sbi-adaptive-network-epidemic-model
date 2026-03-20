#!/usr/bin/env python3
"""
Systematic discriminatory power test for all summary statistics.

For each parameter (beta, gamma, rho), varies it across 4 levels while
holding the others fixed at their midpoint. Generates KDE plots for every
(stat, parameter) combination.

Usage:
    python plot/experiments/discriminatory_power.py
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import product

from analysis.simulate import simulate_summary_stats

# -----------------------------------------------------------------------
# All stats available in the C++ registry
# -----------------------------------------------------------------------
ALL_STATS = [
    "peak_infected_fraction",
    "time_to_peak_infected_fraction",
    "auc_infected_fraction",
    "initial_slope_infected_fraction",
    "total_rewire_count",
    "peak_rewire_count",
    "time_to_peak_rewire_count",
    "mean_degree",
    "sd_degree",
    "lag_peak",
    "cumulative_infected_fraction_until_first_rewire",
]

# -----------------------------------------------------------------------
# Parameter sweep design
# Fix two params at their midpoint, vary the third across 4 levels.
# -----------------------------------------------------------------------
BETA_MID  = 0.20
GAMMA_MID = 0.10
RHO_MID   = 0.30

SWEEP = {
    "rho": {
        "values":  [0.05, 0.20, 0.40, 0.70],
        "fixed":   {"beta": BETA_MID, "gamma": GAMMA_MID},
        "palette": "Blues",
    },
    "beta": {
        "values":  [0.05, 0.15, 0.30, 0.50],
        "fixed":   {"gamma": GAMMA_MID, "rho": RHO_MID},
        "palette": "Oranges",
    },
    "gamma": {
        "values":  [0.02, 0.07, 0.12, 0.20],
        "fixed":   {"beta": BETA_MID, "rho": RHO_MID},
        "palette": "Greens",
    },
}

N_SIM    = 100   # simulations per parameter set
OUT_DIR  = Path("paper/figures/discriminatory_power")


def build_params_list(param_name: str, sweep_cfg: dict) -> list[dict]:
    """Build the params_list for simulate_summary_stats for one parameter sweep."""
    rows = []
    for v in sweep_cfg["values"]:
        row = dict(sweep_cfg["fixed"])
        row[param_name] = v
        rows.append(row)
    return rows


def simulate_all_sweeps(n_sim: int) -> dict[str, pd.DataFrame]:
    """Simulate all three parameter sweeps.

    Returns
    -------
    dict mapping param_name -> DataFrame with columns:
        beta, gamma, rho, stat_0, stat_1, ...
    """
    results = {}
    for param_name, sweep_cfg in SWEEP.items():
        print(f"  Sweeping {param_name} ({len(sweep_cfg['values'])} levels × {n_sim} sims)...")
        params_list = build_params_list(param_name, sweep_cfg)
        df = simulate_summary_stats(params_list, ALL_STATS, n_sim)
        results[param_name] = df
    return results


def plot_single_stat_sweep(
    df:         pd.DataFrame,
    stat:       str,
    param_name: str,
    values:     list,
    palette:    str,
    ax:         plt.Axes,
):
    """KDE plot of one stat for all levels of one parameter on a given Axes."""
    colors = sns.color_palette(palette, n_colors=len(values))

    for val, color in zip(values, colors):
        subset = df[df[param_name].round(4) == round(val, 4)][stat]
        if subset.empty or subset.std() < 1e-10:
            continue
        sns.kdeplot(subset, ax=ax, color=color, label=f"{param_name}={val}", alpha=0.2)

    ax.set_xlabel(stat.replace("_", " "), fontsize=9)
    ax.set_ylabel("")
    ax.legend(fontsize=7, loc="upper right")
    ax.tick_params(labelsize=7)


def plot_all_stats_for_param(
    df:         pd.DataFrame,
    param_name: str,
    sweep_cfg:  dict,
    out_dir:    Path,
):
    """One figure per parameter — all stats as subplots.

    Layout: ceil(n_stats / 3) rows × 3 columns.
    Saves to out_dir/param_name.png
    """
    n_cols = 3
    n_rows = int(np.ceil(len(ALL_STATS) / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 3.5))
    axes_flat = axes.flatten()

    for idx, stat in enumerate(ALL_STATS):
        plot_single_stat_sweep(
            df, stat, param_name,
            sweep_cfg["values"],
            sweep_cfg["palette"],
            axes_flat[idx],
        )
        axes_flat[idx].set_title(stat.replace("_", " "), fontsize=9, pad=4)

    # hide unused axes
    for idx in range(len(ALL_STATS), len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fixed_str = ", ".join(f"{k}={v}" for k, v in sweep_cfg["fixed"].items())
    fig.suptitle(
        f"Discriminatory power — varying {param_name} ({fixed_str})",
        fontsize=12, y=1.01,
    )
    fig.tight_layout()
    file_name = f"{param_name}_stats_discriminatory_power.png"
    fig.savefig(out_dir / file_name, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved {file_name}")


def plot_summary_heatmap(sweep_results: dict[str, pd.DataFrame], out_dir: Path):
    """Heatmap of overlap score for every (stat, parameter) combination.

    Overlap score = 1 - (KL divergence between lowest and highest level).
    Low overlap = high discriminatory power (good).
    High overlap = distributions are similar = stat doesn't separate these values.
    """
    from scipy.stats import gaussian_kde

    def overlap_score(a: np.ndarray, b: np.ndarray) -> float:
        """Estimate distributional overlap between two samples.
        Returns value in [0, 1] — 0 = no overlap, 1 = identical distributions.
        """
        if a.std() < 1e-10 or b.std() < 1e-10:
            return 1.0
        grid = np.linspace(
            min(a.min(), b.min()),
            max(a.max(), b.max()),
            200,
        )
        kde_a = gaussian_kde(a)(grid)
        kde_b = gaussian_kde(b)(grid)
        # overlap coefficient = integral of min(p, q)
        return float(np.trapezoid(np.minimum(kde_a, kde_b), grid))

    rows = []
    for param_name, df in sweep_results.items():
        values   = SWEEP[param_name]["values"]
        low_df   = df[df[param_name].round(4) == round(values[0],  4)]
        high_df  = df[df[param_name].round(4) == round(values[-1], 4)]

        for stat in ALL_STATS:
            score = overlap_score(low_df[stat].values, high_df[stat].values)
            rows.append({
                "stat":      stat,
                "parameter": param_name,
                "overlap":   score,
            })

    pivot = (
        pd.DataFrame(rows)
        .pivot(index="stat", columns="parameter", values="overlap")
    )

    fig, ax = plt.subplots(figsize=(7, max(4, len(ALL_STATS) * 0.55 + 2)))
    sns.heatmap(
        pivot,
        ax=ax,
        annot=True, fmt=".2f",
        cmap="RdYlGn_r",   # red = high overlap (bad), green = low overlap (good)
        vmin=0, vmax=1,
        linewidths=0.5,
    )
    ax.set_title(
        "Distributional overlap (low = good discriminatory power)",
        fontsize=11, pad=10,
    )
    ax.set_xlabel("Parameter")
    ax.set_ylabel("Summary statistic")
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "overlap_heatmap.png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print("  Saved overlap_heatmap.png")

    return pivot


def print_recommendations(pivot: pd.DataFrame):
    """Print which stats have good and poor discriminatory power."""
    print("\nDiscriminatory power summary")
    print("=" * 55)
    print("Overlap score: 0 = fully separated, 1 = identical\n")

    print("Best stats per parameter (lowest overlap):")
    for param in ["beta", "gamma", "rho"]:
        ranked = pivot[param].sort_values()
        best   = ranked.index[0]
        print(f"  {param:6s}: {best:50s} overlap={ranked.iloc[0]:.2f}")

    print("\nStats with poor discriminatory power for all parameters (overlap > 0.8):")
    weak = pivot[pivot.min(axis=1) > 0.8].index.tolist()
    if weak:
        for s in weak:
            print(f"  {s}  — consider removing from active_stats")
    else:
        print("  None — all stats have some discriminatory power")

    print("\nFull overlap table (sorted by min overlap across params):")
    pivot["min_overlap"] = pivot.min(axis=1)
    print(pivot.sort_values("min_overlap").to_string(float_format="{:.2f}".format))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Simulating {len(SWEEP)} parameter sweeps × {len(ALL_STATS)} stats × {N_SIM} sims...")
    sweep_results = simulate_all_sweeps(N_SIM)

    print("\nGenerating per-parameter KDE plots...")
    for param_name, sweep_cfg in SWEEP.items():
        plot_all_stats_for_param(
            sweep_results[param_name],
            param_name,
            sweep_cfg,
            OUT_DIR,
        )

    print("\nGenerating overlap heatmap...")
    pivot = plot_summary_heatmap(sweep_results, OUT_DIR)

    print_recommendations(pivot)
    print(f"\nAll plots saved to {OUT_DIR}")


if __name__ == "__main__":
    main()