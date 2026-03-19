import numpy as np

def regression_adjustment(accepted_params: np.ndarray, accepted_stats: np.ndarray, s_obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Performs regression adjustment on the accepted parameters.

    Parameters
    ----------
    accepted_params: np.ndarray
        The parameters corresponding to the accepted simulations (shape: n_accepted x n_params).
    accepted_stats: np.ndarray
        The summary statistics corresponding to the accepted simulations (shape: n_accepted x n_stats).
    s_obs: np.ndarray
        The observed summary statistics (shape: n_stats,).
    
    Returns
    -------
    adjusted_params: np.ndarray
        The adjusted parameters after regression adjustment (shape: n_accepted x n_params).
    residuals: np.ndarray
        The residuals from the regression (shape: n_accepted x n_params).
    """
    # For simplicity, we will implement a local linear regression adjustment using an Epanechnikov kernel.
    return _local_linear_regression_adjustment(accepted_params, accepted_stats, s_obs, kernel="epanechnikov")


def _local_linear_regression_adjustment(
    accepted_params: np.ndarray,
    accepted_stats: np.ndarray,
    s_obs: np.ndarray,
    kernel: str = "epanechnikov",
) -> tuple[np.ndarray, np.ndarray]:
    """Performs local linear regression adjustment on the accepted parameters.

    Parameters
    ----------
    accepted_params: np.ndarray
        The parameters corresponding to the accepted simulations (shape: n_accepted x n_params).
    accepted_stats: np.ndarray
        The summary statistics corresponding to the accepted simulations (shape: n_accepted x n_stats).
    s_obs: np.ndarray
        The observed summary statistics (shape: n_stats,).
    kernel: str
        The kernel to use for weighting (default: "epanechnikov").
    
    Returns
    -------
    adjusted_params: np.ndarray
        The adjusted parameters after regression adjustment (shape: n_accepted x n_params).
    residuals: np.ndarray
        The residuals from the regression (shape: n_accepted x n_params).

    Reference: Beaumont, M. A., Zhang, W., & Balding, D. J. (2002).
    Approximate Bayesian computation in population genetics. Genetics, 162(4), 2025-2035.
    """
    
    m = accepted_params.shape[0]
    s_diff = accepted_stats - s_obs 
    ones = np.ones(shape=(m, 1))

    X = np.hstack([ones, s_diff])  # add intercept term
    Y = accepted_params         # shape (n_accepted, n_params)

    # Kernel Matrix
    if kernel == "epanechnikov":
        q = 90
        # Epanechnikov kernel weights
        t = np.linalg.norm(s_diff, axis=1)
        delta = np.percentile(t, q)  # use 75th percentile as bandwidth
        w = np.maximum(0, 1 - (t / delta) ** 2)
        w_norm = w / np.sum(w)

        W = np.diag(w_norm)

        # Weighted least squares solution
        Q = X.T @ W @ X
        coeffs = np.linalg.solve(Q, X.T @ W @ Y)
        alpha_hat, beta_hat = coeffs[0], coeffs[1:]
    else:
        raise ValueError(f"Unsupported kernel: {kernel}")
    
    # Adjusted Parameters
    adjusted_params = accepted_params - s_diff @ beta_hat
    residuals = accepted_params - (ones @ alpha_hat + s_diff @ beta_hat)

    return adjusted_params, residuals