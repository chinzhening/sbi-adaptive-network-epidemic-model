#include "summary.hpp"

#include <cmath>

SummaryStatistics compute_summary_statistics(const SimResult& result, const std::vector<StatIndex>& active_stats) {
    SummaryStatistics stats;
    for (StatIndex idx : active_stats) {
        stats[idx] = ALL_STAT_FNS[idx](result);
    }
    return stats;
}

std::vector<SummaryStatistics> compute_summary_statistics(const std::vector<SimResult>& results, const std::vector<StatIndex>& active_stats) {
    int n = results.size();
    std::vector<SummaryStatistics> stats_vec(n);
    for (int i = 0; i < n; ++i) {
        stats_vec[i] = compute_summary_statistics(results[i], active_stats);
    }
    return stats_vec;
}

SummaryStatistics aggregate_summary_statistics(const std::vector<SummaryStatistics>& stats_vec, const std::vector<StatIndex>& active_stats) {
    SummaryStatistics aggregated;
    size_t n = stats_vec.size();
    for (StatIndex idx : active_stats) {
        double sum = 0.0;
        for (const SummaryStatistics& stats : stats_vec) {
            sum += stats[idx];
        }
        aggregated[idx] = sum / static_cast<double>(n);
    }
    return aggregated;
}

inline double peak_infected_fraction(const SimResult& result) {
    double peak = 0.0;
    for (double fraction : result.infected_fraction) {
        if (fraction > peak) {
            peak = fraction;
        }
    }
    return peak;
}

inline double time_to_peak_infected_fraction(const SimResult& result) {
    double peak = peak_infected_fraction(result);
    for (size_t t = 0; t < SIM_T + 1; ++t) {
        if (result.infected_fraction[t] == peak) {
            return static_cast<double>(t);
        }
    }
    return -1.0; // Should not happen if peak_infected_fraction is called correctly

}

inline double auc_infected_fraction(const SimResult& result) {
    double auc = 0.0;
    for (double fraction : result.infected_fraction) {
        auc += fraction;
    }
    return auc;
}

inline double initial_slope_infected_fraction(const SimResult& result) {
    // Average slope over the first few time steps to get a more stable estimate.
    int n_slopes = 5;

    double slope_sum = 0.0;
    for (size_t t = 0; t < n_slopes; ++t) {
        slope_sum += result.infected_fraction[t + 1] - result.infected_fraction[t];
    }
    double avg_slope = slope_sum / static_cast<double>(n_slopes);
    return avg_slope;
}

inline double total_rewire_count(const SimResult& result) {
    double total = 0.0;
    for (double count : result.rewire_counts) {
        total += count;
    }
    return total;
}

inline double peak_rewire_count(const SimResult& result) {
    double peak = 0.0;
    for (double count : result.rewire_counts) {
        if (count > peak) {
            peak = count;
        }
    }
    return static_cast<double>(peak);
}

inline double time_to_peak_rewire_count(const SimResult& result) {
    double peak = peak_rewire_count(result);
    for (size_t t = 0; t < SIM_T + 1; ++t) {
        if (result.rewire_counts[t] == peak) {
            return static_cast<double>(t);
        }
    }
    return -1.0; // Should not happen if peak_rewire_count is called correctly

}

inline double lag_peak(const SimResult& result) {
    double t_peak_infected = time_to_peak_infected_fraction(result);
    double t_peak_rewire = time_to_peak_rewire_count(result);
    return t_peak_infected - t_peak_rewire;
}

inline double mean_degree(const SimResult& result) {
    long long degree_sum = 0;
    long long total_nodes = 0;
    for (size_t bin = 0; bin < SIM_DEG_BINS; ++bin) {
        degree_sum += bin * result.degree_histogram[bin];
        total_nodes += result.degree_histogram[bin];
    }
    return static_cast<double>(degree_sum) / static_cast<double>(total_nodes);
}

inline double sd_degree(const SimResult& result) {
    double mean = mean_degree(result);
    double variance_sum = 0.0;
    long long total_nodes = 0;

    double diff;
    for (size_t bin = 0; bin < SIM_DEG_BINS; ++bin) {
        diff = bin - mean;
        variance_sum += result.degree_histogram[bin] * (diff * diff);
        total_nodes += result.degree_histogram[bin];
    }
    double variance = variance_sum / static_cast<double>(total_nodes);
    return std::sqrt(variance);
}

inline double cumulative_infected_fraction_until_first_rewire(const SimResult& result) {
    int first_rewire_time = -1;
    for (size_t t = 0; t < SIM_T + 1; ++t) {
        if (result.rewire_counts[t] > 0) {
            first_rewire_time = static_cast<int>(t);
            break;
        }
    }
    if (first_rewire_time == -1) {
        return -1.0;
    }

    double cumulative = 0.0;
    for (size_t t = 0; t <= static_cast<size_t>(first_rewire_time); ++t) {
        cumulative += result.infected_fraction[t];
    }
    return cumulative;

}