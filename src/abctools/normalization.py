import numpy as np

def equalize_variance(stats: np.ndarray) -> callable:
    """
    Compute scaling factors to equalize the variance of each summary statistic and apply the scaling.
    Parameters
    ----------
    stats : np.ndarray
        The summary statistics (shape: n_samples x n_stats).

    Returns
    -------
    callable
        A function that takes summary statistics and returns the normalized summary statistics.
    """
    variances = np.var(stats, axis=0)
    scaling_factors = 1 / np.sqrt(variances + 1e-8)
    return lambda s: s * scaling_factors


def median_absolute_deviation(stats: np.ndarray) -> callable:
    """
    Compute scaling factors to equalize the median absolute deviation (MAD) of each summary statistic and apply the scaling.
    Parameters
    ----------
    stats : np.ndarray
        The summary statistics (shape: n_samples x n_stats).

    Returns
    -------
    callable
        A function that takes summary statistics and returns the normalized summary statistics.
    """
    medians = np.median(stats, axis=0)
    mad = np.median(np.abs(stats - medians), axis=0)
    scaling_factors = 1 / (mad + 1e-8)
    return lambda s: s * scaling_factors