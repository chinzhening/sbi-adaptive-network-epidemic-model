#pragma once
#include <string>
#include <vector>

#include "distance.hpp"
#include "normalization.hpp"
#include "summary.hpp"

struct ExperimentConfig {
    std::string name = "experiment";
};

struct PriorConfig {
    double beta_min  = 0.05;
    double beta_max  = 0.5;
    double gamma_min = 0.02;
    double gamma_max = 0.2;
    double rho_min   = 0.0;
    double rho_max   = 0.8;
};

struct ABCConfig {
    int n_simulations = 10000;
    double epsilon    = 1.0;
    Normalization normalization = Normalization::EQUALIZE_VARIANCE;
    DistanceFunction distance = DistanceFunction::EUCLIDEAN;
    std::vector<StatIndex> active_stats;
};

struct IOConfig {
    std::string final_degree_histograms_path = "data/final_degree_histograms.csv";
    std::string infected_timeseries_path     = "data/infected_timeseries.csv";
    std::string rewiring_timeseries_path     = "data/rewiring_timeseries.csv";
    bool run_diagnostics                     = true;
};

struct Config {
    ExperimentConfig experiment;
    PriorConfig      prior;
    ABCConfig        abc;
    IOConfig         io;
};

Normalization parse_normalization(const std::string& s);
DistanceFunction parse_distance(const std::string& s);
StatIndex stat_id_from_string(const std::string& s);

Config load_config(const std::string& path);