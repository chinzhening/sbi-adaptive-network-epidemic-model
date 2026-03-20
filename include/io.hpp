#pragma once
#include <filesystem>
#include <string>
#include <vector>

#include "common.hpp"
#include "summary.hpp"
#include "config.hpp"

std::filesystem::path create_output_dir(const ExperimentConfig& experiment_cfg);

// Save ABC results to CSV
void save_results(
    const std::vector<double>&            beta,
    const std::vector<double>&            gamma,
    const std::vector<double>&            rho,
    const std::vector<SummaryStatistics>& stats,
    const std::vector<StatIndex>&         active_stats,
    const std::vector<double>&            distances,
    const std::vector<bool>&              accepted,
    const std::filesystem::path&          output_dir
);

void save_simulation_results(
    const std::vector<SummaryStatistics>& stats,
    const std::vector<StatIndex>&         active_stats,
    const std::filesystem::path&          output_dir
);

// Load observed data from CSV files specified in config
std::vector<SimResult> load_observed_data(const IOConfig& io_cfg);