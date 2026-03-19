import tomllib
import numpy as np
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ABCResult:
    proposed_params: np.ndarray
    accepted_params: np.ndarray

    simulated_stats: np.ndarray
    accepted_stats: np.ndarray
    observed_stats: np.ndarray
    
    distances: np.ndarray
    accepted_mask: np.ndarray
    acceptance_rate: float
    epsilon: float
    n_simulations: int
    param_names: list[str]

@dataclass
class PlotConfig:
    experiment_name: str
    active_stats:    list[str]
    param_names:     list[str]
    epsilon:         float
    n_simulations:   int

def load_plot_config(config_path: Path) -> PlotConfig:
    """Read config.toml and return a PlotConfig.

    Only extracts the fields the Python diagnostics layer needs.
    The full simulation/prior/io config is irrelevant here since
    the C++ binary has already run and written its output.

    Parameters
    ----------
    path : str | Path
        Path to the config.toml file — should be the copy saved
        inside the run output directory, not the root config.toml,
        so the config always matches the results being analysed.

    Returns
    -------
    PlotConfig
    """
    with open(config_path, 'rb') as f:
        tbl = tomllib.load(f)

    return PlotConfig(
        experiment_name = tbl['experiment']['name'],
        active_stats    = tbl['abc']['active_stats'],
        param_names     = ["beta", "gamma", "rho"],
        epsilon         = tbl['abc']['epsilon'],
        n_simulations   = tbl['abc']['n_simulations'],
    )


def reconstruct_result(results_path: str | Path, cfg: PlotConfig) -> ABCResult:
    """Load abc_results.csv written by the C++ binary and reconstruct an ABCResult.

    The CSV column order is:
        [active_stat_0, ..., active_stat_n, beta, gamma, rho, distance, accepted]

    Parameters
    ----------
    results_path : str | Path
        Path to abc_results.csv
    cfg : PlotConfig
        Config for this run — used to determine column counts and param names.

    Returns
    -------
    ABCResult
    """
    data = np.genfromtxt(results_path, delimiter=",", skip_header=1)

    n_stats  = len(cfg.active_stats)
    n_params = len(cfg.param_names)

    # column slices matching the order save_results writes in io.cpp
    simulated_stats  = data[:, :n_stats]
    proposed_params  = data[:, n_stats:n_stats + n_params]
    distances        = data[:, n_stats + n_params]
    accepted_mask    = data[:, n_stats + n_params + 1].astype(bool)

    accepted_params = proposed_params[accepted_mask]
    accepted_stats  = simulated_stats[accepted_mask]

    return ABCResult(
        proposed_params  = proposed_params,
        accepted_params  = accepted_params,
        simulated_stats  = simulated_stats,
        accepted_stats   = accepted_stats,
        observed_stats   = np.array([]),   # not written to CSV — not needed for diagnostics
        distances        = distances,
        accepted_mask    = accepted_mask,
        acceptance_rate  = accepted_mask.mean(),
        epsilon          = cfg.epsilon,
        n_simulations    = cfg.n_simulations,
        param_names      = cfg.param_names,
    )