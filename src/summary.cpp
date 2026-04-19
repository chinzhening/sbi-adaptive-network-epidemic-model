#include "summary.hpp"

#include <cmath>

DenseStats compute_summary_statistics(const SimResult& result, const StatLayout& layout) {
    DenseStats stats(layout.size());
    for (int idx = 0; idx < layout.size(); ++idx) {
        stats[idx] = ALL_STAT_FNS[layout.active[idx]](result);
    }
    return stats;
}

std::vector<DenseStats> compute_summary_statistics(const std::vector<SimResult>& results, const StatLayout& layout) {
    int n = results.size();
    std::vector<DenseStats> stats_vec(n);
    for (int idx = 0; idx < n; ++idx) {
        stats_vec[idx] = compute_summary_statistics(results[idx], layout);
    }
    return stats_vec;
}

DenseStats aggregate_summary_statistics(
    const std::vector<DenseStats>& stats_vec,
    const StatLayout& layout
) {
    const std::size_t n = layout.size();
    const std::size_t m = stats_vec.size();

    DenseStats agg(2 * n, 0.0);
    DenseStats mean(n, 0.0);
    DenseStats mean2(n, 0.0);

    for (const auto& s : stats_vec) {
        for (std::size_t i = 0; i < n; ++i) {
            mean[i]  += s[i];
            mean2[i] += s[i] * s[i];
        }
    }

    for (std::size_t i = 0; i < n; ++i) {
        const double mu = mean[i] / m;
        const double ex2 = mean2[i] / m;

        agg[i] = mu;
        agg[n + i] = std::sqrt(ex2 - mu * mu);
    }

    return agg;
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

inline double initial_growth_ratio(const SimResult& result) {
    return result.infected_fraction[1] / result.infected_fraction[0];
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

inline double rewire_to_infection_ratio(const SimResult& result) {
    // --- Total rewiring ---
    double total_rewire = 0.0;
    double total_infections = 0.0;
    for (size_t t = 0; t < SIM_T + 1; ++t) {
        total_rewire += result.rewire_counts[t];
        
        double delta = result.infected_fraction[t + 1] - result.infected_fraction[t];
        if (delta > 0.0) {
            total_infections += delta;
        }
    }

    // --- Avoid division by zero ---
    if (total_infections <= 1e-12) {
        return 0.0; 
    }

    return total_rewire / total_infections;
}