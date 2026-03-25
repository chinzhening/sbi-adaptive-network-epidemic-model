#pragma once
#include <vector>
#include "summary.hpp"

enum class DistanceFunction {
    EUCLIDEAN,
};

double compute_distance(const DenseStats& stats1, const DenseStats& stats2, DistanceFunction method);
double euclidean_distance(const DenseStats& stats1, const DenseStats& stats2);