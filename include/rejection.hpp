#pragma once
#include "config.hpp"
#include "result.hpp"

double compute_quantile(const std::vector<double>& data, double quantile);
ABCResult run_abc_rejection(const Config& cfg, const DenseStats& s_obs, const StatLayout& layout);
