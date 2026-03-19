#include <algorithm>
#include <cmath>
#include <stdexcept>

#include "normalization.hpp"

SummaryStatistics apply_scaling(
    const SummaryStatistics& stats,
    const std::vector<double>& normalization_factors,
    const std::vector<StatIndex>& active_stats
) {
    int n_stats = active_stats.size();
    SummaryStatistics normalized_stats;
    for (int j = 0; j < n_stats; ++j) {
        normalized_stats[active_stats[j]] = stats[active_stats[j]] / normalization_factors[j];
    }
    return normalized_stats;
}

std::vector<SummaryStatistics> apply_scaling(
    const std::vector<SummaryStatistics>& stats_vec,
    const std::vector<double>& normalization_factors,
    const std::vector<StatIndex>& active_stats
) {
    std::vector<SummaryStatistics> normalized_stats_vec(stats_vec.size());
    for (size_t i = 0; i < stats_vec.size(); ++i) {
        normalized_stats_vec[i] = apply_scaling(stats_vec[i], normalization_factors, active_stats);
    }
    return normalized_stats_vec;
}


std::vector<double> compute_normalization_scale(
    const std::vector<SummaryStatistics>& stats_vec,
    Normalization method,
    const std::vector<StatIndex>& active_stats
) {
    switch (method) {
        case Normalization::NONE:
            return std::vector<double>(active_stats.size(), 1.0);
        case Normalization::EQUALIZE_VARIANCE:
            return compute_equalize_variance_scale(stats_vec, active_stats);
        case Normalization::EQUALIZE_MAD:
            return compute_equalize_mad_scale(stats_vec, active_stats);
        default:
            throw std::invalid_argument("Unknown normalization method");
    }
}

std::vector<double> compute_equalize_variance_scale(
    const std::vector<SummaryStatistics>& stats_vec,
    const std::vector<StatIndex>& active_stats
) {
    int n_samples = stats_vec.size();
    int n_stats = active_stats.size();
    std::vector<double> mu(n_stats, 0.0);
    std::vector<double> mu2(n_stats, 0.0);
    for (const auto& stats : stats_vec) {
        for (int i = 0; i < n_stats; ++i) {
            mu[i] += stats[active_stats[i]];
            mu2[i] += stats[active_stats[i]] * stats[active_stats[i]];
        }
    }
    for (int i = 0; i < n_stats; ++i) {
        mu[i] /= stats_vec.size();
        mu2[i] /= stats_vec.size();
    }
    std::vector<double> sds(n_stats, 0.0);
    for (int i = 0; i < n_stats; ++i) {
        sds[i] = std::sqrt(mu2[i] - mu[i] * mu[i]);
    }
    return sds;
}

std::vector<double> compute_equalize_mad_scale(
    const std::vector<SummaryStatistics>& stats_vec,
    const std::vector<StatIndex>& active_stats
) {
    int n_samples = stats_vec.size();
    int n_stats = active_stats.size();
    std::vector<double> medians(n_stats, 0.0);
    for (int i = 0; i < n_stats; ++i) {
        std::vector<double> values_i(n_samples);
        for (int j = 0; j < n_samples; ++j) {
            values_i[j] = stats_vec[j][active_stats[i]];
        }
        std::nth_element(values_i.begin(), values_i.begin() + n_samples / 2, values_i.end());
        medians[i] = values_i[n_samples / 2];
    }
    std::vector<double> mad(n_stats, 0.0);
    for (int i = 0; i < n_stats; ++i) {
        std::vector<double> abs_devs(n_samples);
        for (int j = 0; j < n_samples; ++j) {
            abs_devs[j] = std::abs(stats_vec[j][active_stats[i]] - medians[i]);
        }
        std::nth_element(abs_devs.begin(), abs_devs.begin() + n_samples / 2, abs_devs.end());
        mad[i] = abs_devs[n_samples / 2];
    }
    return mad;
}