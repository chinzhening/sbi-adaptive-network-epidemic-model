#include <algorithm>
#include <cmath>
#include <stdexcept>

#include "normalization.hpp"

DenseStats apply_scaling(
    const DenseStats& stats,
    const std::vector<double>& norm_factors
) {
    int n = stats.size();
    DenseStats norm_stats(n, 0.0);
    for (int idx = 0; idx < n; ++idx) {
        norm_stats[idx] = stats[idx] / norm_factors[idx];
    }
    return norm_stats;
}

std::vector<DenseStats> apply_scaling(
    const std::vector<DenseStats>& stats_vec,
    const std::vector<double>& norm_factors
) {
    int n = stats_vec.size();
    std::vector<DenseStats> norm_stats_vec(n);
    for (size_t idx = 0; idx < n; ++idx) {
        norm_stats_vec[idx] = apply_scaling(stats_vec[idx], norm_factors);
    }
    return norm_stats_vec;
}


std::vector<double> compute_normalization_scale(
    const std::vector<DenseStats>& stats_vec,
    Normalization method,
    int n_stats
) {
    switch (method) {
        case Normalization::NONE:
            return std::vector<double>(n_stats, 1.0);
        case Normalization::EQUALIZE_VARIANCE:
            return compute_equalize_variance_scale(stats_vec, n_stats);
        case Normalization::EQUALIZE_MAD:
            return compute_equalize_mad_scale(stats_vec, n_stats);
        default:
            throw std::invalid_argument("Unknown normalization method");
    }
}

std::vector<double> compute_equalize_variance_scale(
    const std::vector<DenseStats>& stats_vec,
    int n_stats
) {
    int n_samples = stats_vec.size();
    std::vector<double> mu(n_stats, 0.0);
    std::vector<double> mu2(n_stats, 0.0);
    std::vector<double> sd(n_stats, 0.0);
    for (const auto& s : stats_vec) {
        for (int idx = 0; idx < n_stats; ++idx) {
            mu[idx] += s[idx];
            mu2[idx] += s[idx] * s[idx];
        }
    }
    for (int idx = 0; idx < n_stats; ++idx) {
        mu[idx] /= stats_vec.size();
        mu2[idx] /= stats_vec.size();
        sd[idx] = std::sqrt(mu2[idx] - mu[idx] * mu[idx]);
    }
    return sd;
}

std::vector<double> compute_equalize_mad_scale(
    const std::vector<DenseStats>& stats_vec,
    int n_stats
) {
    int n_samples = stats_vec.size();
    std::vector<double> medians(n_stats, 0.0);
    for (int idx = 0; idx < n_stats; ++idx) {
        std::vector<double> values_i(n_samples);
        for (int j = 0; j < n_samples; ++j) {
            values_i[j] = stats_vec[j][idx];
        }
        std::nth_element(values_i.begin(), values_i.begin() + n_samples / 2, values_i.end());
        medians[idx] = values_i[n_samples / 2];
    }
    std::vector<double> mad(n_stats, 0.0);
    for (int idx = 0; idx < n_stats; ++idx) {
        std::vector<double> abs_devs(n_samples);
        for (int j = 0; j < n_samples; ++j) {
            abs_devs[j] = std::abs(stats_vec[j][idx] - medians[idx]);
        }
        std::nth_element(abs_devs.begin(), abs_devs.begin() + n_samples / 2, abs_devs.end());
        mad[idx] = abs_devs[n_samples / 2];
    }
    return mad;
}