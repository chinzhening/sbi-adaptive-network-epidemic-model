import subprocess
import numpy as np
import pandas as pd

from pathlib import Path
import tempfile

BINARY = "./build/simulate"

def simulate(
    beta:        float,
    gamma:       float,
    rho:         float,
    n_sim:       int,
    stat_names:  list[str],
    output_dir:  str | None = None,
) -> dict:
    """Run the C++ simulator for a single parameter set and return results as numpy arrays.

    Parameters
    ----------
    beta, gamma, rho : float
        Model parameters.
    n_sim : int
        Number of simulations to run.
    stat_names : list[str]
        Names of the summary statistics to compute.
    output_dir : str | None
        Where to write CSV output. If None, uses a temp directory that is
        cleaned up after loading. Pass a path if you want to keep the files.
    binary : str
        Path to the simulate binary.

    Returns
    -------
    dict with keys:
        "summary_stats"      : pd.DataFrame, shape (n_sim, n_active_stats)
        "output_dir"         : str — path to the output files
    """
    cleanup = False
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
        cleanup    = True

    result = subprocess.run([
        BINARY,
        "--beta",   str(beta),
        "--gamma",  str(gamma),
        "--rho",    str(rho),
        "--n_sim",  f"{n_sim}",
        "--stats",  *stat_names,
        "--output", output_dir,
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"simulate failed:\n{result.stderr}")

    out = Path(output_dir)

    data = {
        "summary_stats":     pd.read_csv(out / "simulation_summary.csv"),
        "output_dir":        str(out),
    }

    if cleanup:
        import shutil
        shutil.rmtree(output_dir)

    return data


def simulate_summary_stats(
    params_list: list[dict],
    stat_names:  list[str],
    n_sim:       int,
) -> pd.DataFrame:
    """Simulate multiple parameter sets and return their summary stats side by side.

    Useful for visually checking whether a summary stat separates
    different parameter regimes.

    Parameters
    ----------
    params_list : list of dicts, each with keys "beta", "gamma", "rho"
        e.g. [{"beta": 0.1, "gamma": 0.08, "rho": 0.05},
               {"beta": 0.1, "gamma": 0.08, "rho": 0.4}]
    stat_names : list of str
        Names of the summary statistics to compute.
    n_sim : int
        Number of simulations to run for each parameter set.

    binary : str
        Path to the simulate binary.

    Returns
    -------
    pd.DataFrame
        Each row is one replicate from one parameter set.
        Columns: beta, gamma, rho, plus one column per active stat.
    """
    all_rows = []
    for params in params_list:
        data = simulate(
            beta=params["beta"],
            gamma=params["gamma"],
            rho=params["rho"],
            n_sim=n_sim,
            stat_names=stat_names
        )
        df = data["summary_stats"]
        df["beta"]  = params["beta"]
        df["gamma"] = params["gamma"]
        df["rho"]   = params["rho"]
        all_rows.append(df)

    return pd.concat(all_rows, ignore_index=True)