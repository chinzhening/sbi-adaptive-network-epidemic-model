#pragma once
#include <array>
#include <string>
#include "common.hpp"

// Infected fraction based summaries
inline double peak_infected_fraction(const SimResult& result);
inline double time_to_peak_infected_fraction(const SimResult& result);
inline double auc_infected_fraction(const SimResult& result);
inline double initial_slope_infected_fraction(const SimResult& result);

// Rewire count based summaries
inline double total_rewire_count(const SimResult& result);
inline double peak_rewire_count(const SimResult& result);
inline double time_to_peak_rewire_count(const SimResult& result);

// Degree Histogram based summaries
inline double mean_degree(const SimResult& result);
inline double sd_degree(const SimResult& result);

inline double lag_peak(const SimResult& result);
inline double cumulative_infected_fraction_until_first_rewire(const SimResult& result);


// Array of function pointers for all summary statistics, indexed by StatIndex

enum StatIndex : int {
    PEAK_INFECTED_FRACTION              = 0,
    TIME_TO_PEAK_INFECTED_FRACTION      = 1,
    AUC_INFECTED_FRACTION               = 2,
    INITIAL_SLOPE_INFECTED_FRACTION     = 3,
    TOTAL_REWIRE_COUNT                  = 4,
    PEAK_REWIRE_COUNT                   = 5,
    TIME_TO_PEAK_REWIRE_COUNT           = 6,
    MEAN_DEGREE                         = 7,
    SD_DEGREE                           = 8,
    LAG_PEAK                            = 9,
    CUMULATIVE_INFECTED_FRACTION_UNTIL_FIRST_REWIRE = 10,
    N_STATS                             // sentinel — always last
};

static const std::array<std::string, N_STATS> STAT_NAMES = {
    "peak_infected_fraction",
    "time_to_peak_infected_fraction",
    "auc_infected_fraction",
    "initial_slope_infected_fraction",
    "total_rewire_count",
    "peak_rewire_count",
    "time_to_peak_rewire_count",
    "mean_degree",
    "sd_degree",
    "lag_peak",
    "cumulative_infected_fraction_until_first_rewire"
};

// Struct to hold all summary statistics for a single simulation result
struct SummaryStatistics {
    std::array<double, N_STATS> values{};
    double& operator[](int i)       { return values[i]; }
    double  operator[](int i) const { return values[i]; }
};

// Entry point for computing all summary statistics from a SimResult
SummaryStatistics compute_summary_statistics(const SimResult& result, const std::vector<StatIndex> &active_stats);
SummaryStatistics aggregate_summary_statistics(const std::vector<SummaryStatistics>& stats_vec, const std::vector<StatIndex> &active_stats);

std::vector<SummaryStatistics> compute_summary_statistics(const std::vector<SimResult>& results, const std::vector<StatIndex> &active_stats);

using StatFn = double(*)(const SimResult&);

static const std::array<StatFn, N_STATS> ALL_STAT_FNS = {
    peak_infected_fraction,
    time_to_peak_infected_fraction,
    auc_infected_fraction,
    initial_slope_infected_fraction,
    total_rewire_count,
    peak_rewire_count,
    time_to_peak_rewire_count,
    mean_degree,
    sd_degree,
    lag_peak,
    cumulative_infected_fraction_until_first_rewire
};
