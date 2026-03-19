#pragma once
#include <vector>
#include "summary.hpp"

enum class Normalization {
    NONE,
    EQUALIZE_VARIANCE,
    EQUALIZE_MAD,
};

SummaryStatistics apply_scaling(const SummaryStatistics& stats, const std::vector<double>& normalization_factors, const std::vector<StatIndex>& active_stats);
std::vector<SummaryStatistics> apply_scaling(const std::vector<SummaryStatistics>& stats_vec, const std::vector<double>& normalization_factors, const std::vector<StatIndex>& active_stats);

std::vector<double> compute_normalization_scale(const std::vector<SummaryStatistics>& stats_vec, Normalization method, const std::vector<StatIndex>& active_stats);
std::vector<double> compute_equalize_variance_scale(const std::vector<SummaryStatistics>& stats_vec, const std::vector<StatIndex>& active_stats);
std::vector<double> compute_equalize_mad_scale(const std::vector<SummaryStatistics>& stats_vec, const std::vector<StatIndex>& active_stats);