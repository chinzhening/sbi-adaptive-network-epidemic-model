#include "io.hpp"
#include "summary.hpp"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

std::filesystem::path create_output_dir(const ExperimentConfig& exp_cfg) {
    // build timestamp string: 20240315_143022
    auto now  = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    std::ostringstream ts;
    ts << std::put_time(std::localtime(&time), "%Y%m%d_%H%M%S");

    std::filesystem::path dir = 
        std::filesystem::path("results") / exp_cfg.name / ts.str();

    std::filesystem::create_directories(dir);
    std::cout << "Output directory: " << dir << "\n";
    return dir;
}

void save_results(
    const std::vector<double>&            beta,
    const std::vector<double>&            gamma,
    const std::vector<double>&            rho,
    const std::vector<DenseStats>&        stats,
    const StatLayout&                     layout,
    const std::vector<double>&            distances,
    const std::vector<bool>&              accepted,
    const std::filesystem::path&          output_dir
) {
    auto filepath = output_dir / "abc_results.csv";
    std::ofstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filepath << "\n";
        return;
    }

    // Headers
    int k = layout.size();
    for (size_t i = 0; i < layout.size(); ++i) {
        file << "mean:" << STAT_NAMES[layout.active[i]];
        file << "," << "sd:" << STAT_NAMES[layout.active[i]];
        if (i < k - 1) file << ",";
    }
    file << ",beta,gamma,rho,distance,accepted\n";

    // Data
    for (size_t i = 0; i < stats.size(); ++i) {
        for (size_t j = 0; j < k; ++j) {
            file << stats[i][j];
            file << "," << stats[i][j + k];
            if (j < k - 1) file << ",";
        }
        file << ","  << beta[i]
             << ","  << gamma[i]
             << ","  << rho[i]
             << ","  << distances[i]
             << ","  << accepted[i]
             << "\n";
    }
}

std::vector<SimResult> load_observed_data(const IOConfig& io_cfg) {
    std::vector<SimResult> results(SIM_N_REPLICATES);

    // --- degree histograms ---
    std::ifstream deg_file(io_cfg.final_degree_histograms_path);
    if (!deg_file.is_open()) {
        std::cerr << "Error opening: " << io_cfg.final_degree_histograms_path << "\n";
        return results;
    }
    std::string line;
    std::getline(deg_file, line); // skip header
    while (std::getline(deg_file, line)) {
        std::istringstream ss(line);
        int rep, deg; long long count; char comma;
        ss >> rep >> comma >> deg >> comma >> count;
        if (rep >= 0 && rep < SIM_N_REPLICATES && deg >= 0 && deg < SIM_DEG_BINS)
            results[rep].degree_histogram[deg] = count;
    }

    // --- infected fraction timeseries ---
    std::ifstream inf_file(io_cfg.infected_timeseries_path);
    if (!inf_file.is_open()) {
        std::cerr << "Error opening: " << io_cfg.infected_timeseries_path << "\n";
        return results;
    }
    std::getline(inf_file, line);
    while (std::getline(inf_file, line)) {
        std::istringstream ss(line);
        int rep, t; double val; char c;
        ss >> rep >> c >> t >> c >> val;
        if (rep >= 0 && rep < SIM_N_REPLICATES && t >= 0 && t <= SIM_T)
            results[rep].infected_fraction[t] = val;
    }

    // --- rewire timeseries ---
    std::ifstream rew_file(io_cfg.rewiring_timeseries_path);
    if (!rew_file.is_open()) {
        std::cerr << "Error opening: " << io_cfg.rewiring_timeseries_path << "\n";
        return results;
    }
    std::getline(rew_file, line);
    while (std::getline(rew_file, line)) {
        std::istringstream ss(line);
        int rep, t; long long val; char c;
        ss >> rep >> c >> t >> c >> val;
        if (rep >= 0 && rep < SIM_N_REPLICATES && t >= 0 && t <= SIM_T)
            results[rep].rewire_counts[t] = val;
    }

    return results;
}

void save_simulation_results(
    const std::vector<DenseStats>&        stats,
    const StatLayout&                     layout,
    const std::filesystem::path&          output_dir,
    const std::string                     filename
) {
    // summary statistics
    auto stat_filepath = output_dir / filename;
    std::ofstream out(stat_filepath);
    if (!out.is_open()) {
        std::cerr << "Error opening file for writing: " << stat_filepath << "\n";
        return;
    }

    // Write header
    int k = layout.size();
    for (int i = 0; i < k; ++i) {
        out << "mean:" << STAT_NAMES[layout.active[i]];
        out << ",sd:" << STAT_NAMES[layout.active[i]];
        if (i < k - 1) out << ",";
    }
    out << "\n";
    for (int r = 0; r < (int)stats.size(); ++r) {
        for (int i = 0; i < k; ++i) {
            out << stats[r][i] << "," << stats[r][i + k];
            if (i < k - 1) out << ",";
        }
        out << "\n";
    }
}