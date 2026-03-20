import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from config import ABCResult
from scipy.stats import gaussian_kde

def generate_diagnostics(result: ABCResult) -> tuple[dict, dict]:
    """Generate all diagnostic plots and posterior statistics for a run.

    Calls each individual plot function and packages the results.

    Parameters
    ----------
    result : ABCResult

    Returns
    -------
    diagnostics : dict
        Keys: "distance_histogram", "accepted_params_pairwise_plot",
              "params_kde_and_ci". Values are matplotlib Figure objects.
    posterior_stats : dict
        Keys: param names. Values: dicts with "mean", "kde_mode",
              "ci_lower", "ci_upper".
    """
    betas  = result.accepted_params[:, 0]
    gammas = result.accepted_params[:, 1]
    rhos   = result.accepted_params[:, 2]

    diagnostics = {
        "distance_histogram":            plot_distance_histogram(result.distances, result.epsilon),
        "accepted_params_pairwise_plot": plot_pairwise(betas, gammas, rhos),
        "params_kde_and_ci":             plot_kde_and_ci(betas, gammas, rhos),
    }

    posterior_stats = compute_posterior_stats(betas, gammas, rhos)

    return diagnostics, posterior_stats

def plot_kde_and_ci(betas, gammas, rhos, point_color="black"):
    """
    Generates KDE plots and confidence intervals for the accepted parameters.

    Parameters
    ----------
    betas: array-like, accepted beta parameters
    gammas: array-like, accepted gamma parameters
    rhos: array-like, accepted rho parameters
    point_color: str, color of the KDE plot

    Returns
    -------
    fig: matplotlib.figure.Figure
        The generated figure containing KDE plots and confidence intervals for the parameters.

    """
    fig, ax = plt.subplots(1, 3, figsize=(18, 5))
    param_names = ['beta', 'gamma', 'rho']
    for i, (param, name) in enumerate(zip([betas, gammas, rhos], param_names)):
        sns.kdeplot(param, ax=ax[i], color=point_color)
        ci_lower = np.percentile(param, 2.5)
        ci_upper = np.percentile(param, 97.5)
        ax[i].axvline(ci_lower, color='red', linestyle='--', label='95% CI')
        ax[i].axvline(ci_upper, color='red', linestyle='--')
        ax[i].set_title(f'KDE and 95% CI for {name}')
        ax[i].legend()
    
    fig.tight_layout()
    return fig

def compute_posterior_stats(betas, gammas, rhos):
    """
    Generates posterior statistics (mean, mode, 95% CI) for the accepted parameters.
    
    Parameters
    ----------
    betas: array-like, accepted beta parameters
    gammas: array-like, accepted gamma parameters
    rhos: array-like, accepted rho parameters

    Returns
    -------
    posterior_stats: dict
        A dictionary containing the posterior statistics for each parameter.

    """
    beta_stats = _compute_stat(betas)
    gamma_stats = _compute_stat(gammas)
    rho_stats = _compute_stat(rhos)

    return {
        'beta': beta_stats,
        'gamma': gamma_stats,
        'rho': rho_stats
    }


def _compute_stat(data):
    """
    Helper function to generate mean, mode, and 95% CI for a given parameter data.
    """
    kde = gaussian_kde(data)
    x = np.linspace(min(data), max(data), 500)
    density = kde(x)
    mean = np.mean(data)
    mode = x[np.argmax(density)]
    ci_lower = np.percentile(data, 2.5)
    ci_upper = np.percentile(data, 97.5)
    return {
        'mean': mean,
        'kde_mode': mode,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }


def plot_distance_histogram(distances, epsilon, bins=50, color='black'):
    """
    Plots a histogram of distances with an epsilon threshold line.
    
    Parameters
    ----------
    distances: array-like, distances of proposals to observed summary statistics
    epsilon: float, threshold value for acceptance
    bins: int, number of histogram bins
    color: str, color of histogram bars

    Returns
    -------
    fig: matplotlib.figure.Figure
    """
    # Mask distances to focus on those not too far from the bulk of the distribution
    threshold = min(epsilon * 10, np.quantile(distances, 0.95))  # cap at 10*epsilon or 95th percentile
    distances_masked = distances[distances <= threshold]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(distances_masked, bins=bins, color=color, alpha=0.7)
    ax.axvline(epsilon, color='red', linestyle='--', label='Epsilon Threshold')
    ax.set_xlabel('Distance')
    ax.set_ylabel('Frequency')
    ax.set_title('Histogram of Distances of Proposals to Observed Summary Statistics')
    ax.legend()
    fig.tight_layout()
    return fig


def plot_pairwise(betas, gammas, rhos, point_color='black', diag_color='black'):
    """
    Plots pairwise scatter plots of accepted parameters with histograms on the diagonal.
    
    Parameters
    ----------
    betas: array-like, accepted beta parameters
    gammas: array-like, accepted gamma parameters
    rhos: array-like, accepted rho parameters
    point_color: str, color of scatter points
    diag_color: str, color of diagonal histograms
    
    Returns
    -------
    fig: matplotlib.figure.Figure
        The generated pairwise scatter plot figure.

    """
    accepted_params = pd.DataFrame({
        'beta': betas,
        'gamma': gammas,
        'rho': rhos
    })
    
    g = sns.pairplot(
        accepted_params,
        diag_kind='hist',
        corner=True,
        plot_kws={'color': point_color},
        diag_kws={'color': diag_color}
    )
    g.figure.suptitle('Pairwise Scatter Plot of Accepted Parameters', y=1.02)
    g.figure.tight_layout()
    
    return g.figure