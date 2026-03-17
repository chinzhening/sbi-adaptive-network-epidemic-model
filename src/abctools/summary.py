import numpy as np

def mean_peak_infected(sim_data):
    """Compute the mean peak infected fraction across replicates."""
    infected_fraction, _, _ = sim_data
    return np.mean(np.max(infected_fraction, axis=1))

def mean_time_to_peak_infected(sim_data):
    """Compute the mean time to peak infected fraction across replicates."""
    infected_fraction, _, _ = sim_data
    return np.mean(np.argmax(infected_fraction, axis=1))

def mean_auc_infected(sim_data):
    """Compute the mean area under the curve (AUC) of infected fraction across replicates."""
    infected_fraction, _, _ = sim_data
    return np.mean(np.sum(infected_fraction, axis=1))

def mean_initial_slope_infected(sim_data):
    """Compute the mean initial slope of infected fraction across replicates."""
    infected_fraction, _, _ = sim_data
    n_replicates, T1 = infected_fraction.shape
    initial_slopes = np.zeros(n_replicates)
    for r in range(n_replicates):
        slope = 0.0
        n_points = min(10, T1-1)
        for t in range(n_points):
            slope += infected_fraction[r, t+1] - infected_fraction[r, t]
        initial_slopes[r] = slope / n_points
    return np.mean(initial_slopes)

def mean_total_rewire(sim_data):
    """Compute the mean total number of rewires across replicates."""
    _, rewire_counts, _ = sim_data
    return np.mean(np.sum(rewire_counts, axis=1))

def mean_time_to_peak_rewire(sim_data):
    """Compute the mean time to peak rewires across replicates."""
    _, rewire_counts, _ = sim_data
    return np.mean(np.argmax(rewire_counts, axis=1))

def mean_lag_peak(sim_data):
    """Compute the mean lag between peak infected fraction and peak rewires across replicates."""
    infected_fraction, rewire_counts, _ = sim_data
    peak_infected_times = np.argmax(infected_fraction, axis=1)
    peak_rewire_times = np.argmax(rewire_counts, axis=1)
    return np.mean(peak_rewire_times - peak_infected_times)

def mean_degree(sim_data):
    """Compute the mean and standard deviation of the degree histogram across replicates."""
    _, _, degree_histogram = sim_data
    agg_degree_histogram = np.mean(degree_histogram, axis=0)
    k = np.arange(len(agg_degree_histogram))
    agg_degree_hist_sum = np.sum(agg_degree_histogram)
    mu = np.sum(k * agg_degree_histogram) / agg_degree_hist_sum
    return mu

def sd_degree(sim_data):
    """Compute the standard deviation of the degree histogram across replicates."""
    _, _, degree_histogram = sim_data
    agg_degree_histogram = np.mean(degree_histogram, axis=0)
    k = np.arange(len(agg_degree_histogram))
    agg_degree_hist_sum = np.sum(agg_degree_histogram)
    mu = np.sum(k * agg_degree_histogram) / agg_degree_hist_sum
    mu2 = np.sum(k**2 * agg_degree_histogram) / agg_degree_hist_sum
    sd_degree = np.sqrt(mu2 - mu**2)
    return sd_degree

def mean_cumulative_infected_fraction_until_first_rewire(sim_data):
    """Compute the mean cumulative infected fraction until the first rewire event across replicates."""
    infected_fraction, rewire_count, _ = sim_data
    first_rewire_index = np.argmax(rewire_count > 0, axis=1)

    k = first_rewire_index.shape[0]
    for i in range(k):
        if first_rewire_index[i] == 0:
            # if there is no rewire event, use the entire time series
            first_rewire_index[i] = infected_fraction.shape[1] - 1

    cum_sum_infected_fraction = np.cumsum(infected_fraction, axis=1)
    mean = np.mean([cum_sum_infected_fraction[i, first_rewire_index[i]] for i in range(k)])
    return mean