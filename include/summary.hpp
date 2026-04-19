#pragma once
#include <array>
#include <string>
#include "common.hpp"

// Infected fraction based summaries
inline double peak_infected_fraction(const SimResult& result);
inline double time_to_peak_infected_fraction(const SimResult& result);
inline double auc_infected_fraction(const SimResult& result);
inline double final_infected_fraction(const SimResult& result);
inline double initial_growth_ratio(const SimResult& result);

// Rewire count based summaries
inline double total_rewire_count(const SimResult& result);
inline double peak_rewire_count(const SimResult& result);
inline double time_to_peak_rewire_count(const SimResult& result);

// Degree Histogram based summaries
inline double mean_degree(const SimResult& result);
inline double sd_degree(const SimResult& result);

// Combination summaries
inline double lag_peak(const SimResult& result);
inline double rewire_to_infection_ratio(const SimResult& result);

// Array of function pointers for all summary statistics, indexed by StatIndex

enum StatIndex : int {
    PEAK_INFECTED_FRACTION                = 0,
    TIME_TO_PEAK_INFECTED_FRACTION        = 1,
    AUC_INFECTED_FRACTION                 = 2,
    FINAL_INFECTED_FRACTION               = 3,
    INITIAL_GROWTH_RATIO                  = 4,
    TOTAL_REWIRE_COUNT                    = 5,
    PEAK_REWIRE_COUNT                     = 6,
    TIME_TO_PEAK_REWIRE_COUNT             = 7,
    MEAN_DEGREE                           = 8,
    SD_DEGREE                             = 9,
    LAG_PEAK                              = 10,
    REWIRE_TO_INFECTION_RATIO             = 11,
    N_STATS                             // sentinel — always last
};

static const std::array<std::string, N_STATS> STAT_NAMES = {
    "peak_infected_fraction",
    "time_to_peak_infected_fraction",
    "auc_infected_fraction",
    "final_infected_fraction",
    "initial_growth_ratio",
    "total_rewire_count",
    "peak_rewire_count",
    "time_to_peak_rewire_count",
    "mean_degree",
    "sd_degree",
    "lag_peak",
    "rewire_to_infection_ratio"
};

using StatFn = double(*)(const SimResult&);

static const std::array<StatFn, N_STATS> ALL_STAT_FNS = {
    peak_infected_fraction,
    time_to_peak_infected_fraction,
    auc_infected_fraction,
    final_infected_fraction,
    initial_growth_ratio,
    total_rewire_count,
    peak_rewire_count,
    time_to_peak_rewire_count,
    mean_degree,
    sd_degree,
    lag_peak,
    rewire_to_infection_ratio
};

/** 
 * Established once from config. Passed by const-ref to every pipeline function.
 */
struct StatLayout {
    std::vector<StatIndex> active;
    int size() const { return static_cast<int>(active.size()); }
};

// Type alias for a vector of summary statistics values, used for output formatting
using DenseStats = std::vector<double>;

DenseStats compute_summary_statistics(
    const SimResult& result,
    const StatLayout& layout);

std::vector<DenseStats> compute_summary_statistics(
    const std::vector<SimResult>& results,
    const StatLayout& layout);


DenseStats aggregate_summary_statistics(
    const std::vector<DenseStats>& stats_vec,
    const StatLayout& layout);
