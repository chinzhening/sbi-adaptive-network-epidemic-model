#include "distance.hpp"
#include <cmath>
#include <stdexcept>

double compute_distance(const DenseStats& stats1, const DenseStats& stats2, DistanceFunction method) {
    switch (method) {
        case DistanceFunction::EUCLIDEAN:
            return euclidean_distance(stats1, stats2);
        default:
            throw std::invalid_argument("Unsupported distance function");
    }
}

double euclidean_distance(const DenseStats& stats1, const DenseStats& stats2) {
    double sum_sq = 0.0;
    for (int i = 0; i < (int)stats1.size(); ++i) {
        double diff = stats1[i] - stats2[i];
        sum_sq += diff * diff;
    }
    return std::sqrt(sum_sq);
}