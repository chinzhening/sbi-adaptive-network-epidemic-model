#pragma once
#include <vector>
#include "summary.hpp"

struct ABCResult {
    std::vector<double> beta;
    std::vector<double> gamma;
    std::vector<double> rho;
    std::vector<SummaryStatistics> stats;
    std::vector<double> distances;
    std::vector<bool> accepted;
    double acceptance_rate;
    double epsilon;
    double runtime_seconds;
};