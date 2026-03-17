import pandas as pd
import pickle
import yaml

from .abctools.config import ABCConfig, ABCResult

from pathlib import Path
from datetime import datetime
from functools import lru_cache

CONFIG_PATH = Path("config.yml")

@lru_cache
def _load_global_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)
    

def load_observed_data():
    cfg = _load_global_config()

    data_paths = cfg["data_dir"]
    
    infected_timeseries_data = pd.read_csv(data_paths["infected_timeseries"])
    rewiring_timeseries_data = pd.read_csv(data_paths["rewiring_timeseries"])
    final_degree_histograms_data = pd.read_csv(data_paths["final_degree_histograms"])

    obs_infected_fraction = infected_timeseries_data.pivot(
        index="replicate_id", columns="time", values="infected_fraction"
    ).to_numpy()

    obs_rewire_count = rewiring_timeseries_data.pivot(
        index="replicate_id", columns="time", values="rewire_count"
    ).to_numpy()

    obs_degree_histogram = final_degree_histograms_data.pivot(
        index="replicate_id", columns="degree", values="count"
    ).to_numpy()

    return obs_infected_fraction, obs_rewire_count, obs_degree_histogram



def create_results_dir(experiment_name: str) -> Path:
    """
    Create a timestamped results directory 

    Creates: results/<experiment_name>/<timestamp>/
    """

    cfg = _load_global_config()
    results_root = cfg["results_dir"]

    # Timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results_dir = Path(results_root) / experiment_name / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)

    return results_dir


def save_result(result: ABCResult, results_dir: Path) -> None:
    """
    Save ABCResult object.
    """

    path = results_dir / "result.pkl"

    with open(path, "wb") as f:
        pickle.dump(result, f)


def save_config_reference(config_module: str, results_dir: Path) -> None:
    """
    Save which config was used.
    """

    with open(results_dir / "config.txt", "w") as f:
        f.write(config_module)


def save_fig(fig, results_dir: Path, filename: str) -> Path:
    """
    Save a matplotlib Figure to the results folder.
    
    Parameters
    ----------
    fig: matplotlib Figure object
    results_dir: Path to the results directory
    filename: str, filename to save as (e.g., 'distance_histogram.png')
    
    Returns
    -------
    save_path: Path to the saved figure
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    save_path = results_dir / filename
    fig.savefig(save_path, bbox_inches='tight', dpi=300)

    return save_path

def load_result(path: str) -> ABCResult:
    """
    Load previously saved ABCResult.
    """

    with open(path, "rb") as f:
        return pickle.load(f)
    

def log_experiment(config: ABCConfig, result: ABCResult, results_dir: Path) -> None:
    """
    Log experiment details and results to a text file in the results directory.

    Parameters
    ----------
    config: ABCConfig object containing the experiment configuration
    result: ABCResult object containing the experiment results
    results_dir: Path to the results directory where the log should be saved

    
    """

    log_path = results_dir / "log.txt"

    with open(log_path, "w") as f:
        f.write(f"Experiment Config:\n")
        f.write(f"Simulate function: {config.simulate.__name__}\n")
        f.write(f"Prior function: {config.prior.__name__}\n")
        f.write(f"Summary statistics:\n")
        for stat in config.summary_stats:
            f.write(f"- {stat.__name__}\n")
        f.write(f"Normalization function: {config.normalization.__name__}\n")
        f.write(f"Distance function: {config.distance.__name__}\n")
        f.write(f"Epsilon: {config.epsilon}\n")
        f.write(f"Number of simulations: {config.n_simulations}\n")
        f.write(f"Parameter names: {config.param_names}\n\n")

        f.write(f"Experiment Results:\n")
        f.write(f"Acceptance rate: {result.acceptance_rate:.4f}\n")
        f.write(f"Epsilon threshold: {result.epsilon}\n")
        f.write(f"Number of simulations: {result.n_simulations}\n")
        f.write(f"Runtime (seconds): {result.runtime_seconds:.2f}\n")