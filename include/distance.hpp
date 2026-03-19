#pragma once
#include <vector>
#include "summary.hpp"

enum class DistanceFunction {
    EUCLIDEAN,
};

double compute_distance(const SummaryStatistics& stats1, const SummaryStatistics& stats2, DistanceFunction method);
double euclidean_distance(const SummaryStatistics& stats1, const SummaryStatistics& stats2);