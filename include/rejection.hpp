#pragma once
#include "config.hpp"
#include "result.hpp"

ABCResult run_abc_rejection(const Config& cfg, const DenseStats& s_obs, const StatLayout& layout);
