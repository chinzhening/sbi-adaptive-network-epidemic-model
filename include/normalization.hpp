#pragma once
#include <vector>
#include "summary.hpp"

enum class Normalization {
    NONE,
    EQUALIZE_VARIANCE,
    EQUALIZE_MAD,
};

DenseStats apply_scaling(const DenseStats& stats, const std::vector<double>& normalization_factors);
std::vector<DenseStats> apply_scaling(const std::vector<DenseStats>& stats_vec, const std::vector<double>& normalization_factors);

std::vector<double> compute_normalization_scale(const std::vector<DenseStats>& stats_vec, Normalization method, int n_stats);
std::vector<double> compute_equalize_variance_scale(const std::vector<DenseStats>& stats_vec, int n_stats);
std::vector<double> compute_equalize_mad_scale(const std::vector<DenseStats>& stats_vec, int n_stats);