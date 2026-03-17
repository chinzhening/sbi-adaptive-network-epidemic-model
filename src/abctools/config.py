import numpy as np

from dataclasses import dataclass


@dataclass
class ABCConfig:
    simulate:           callable           # (params)  -> simulated data
    prior:              callable           # ()        -> sampled params dict
    summary_stats:      list[callable]     # list of functions to compute summary stats
    normalization:      callable           # (stats)   -> (stats -> scaled_stats)
    distance:           callable           # (s_obs, s_sim) -> float
    epsilon:            float
    n_simulations:      int
    param_names:        list
    observed_data:      np.ndarray

    def summarize(self, data) -> np.ndarray:
        """
        Compute summary statistics for given data using the configured summary_stats functions.
        """
        return np.array([stat(data) for stat in self.summary_stats])


@dataclass
class ABCResult:
    proposed_params:    np.ndarray         # shape (n_sims, n_params)
    accepted_params:    np.ndarray         # shape (n_acc, n_params)

    simulated_stats:    np.ndarray | None  # shape (n_sims, n_stats)
    accepted_stats:     np.ndarray         # shape (n_acc, n_stats)
    observed_stats:     np.ndarray
    
    distances:          np.ndarray         # shape (n_simulations,)
    accepted_mask:      np.ndarray         # shape (n_simulations,)

    acceptance_rate:    float
    epsilon:            float
    n_simulations:      int
    param_names:        list

    runtime_seconds:    float | None = None

    