#pragma once
#include <vector>
#include <cstdint>

inline constexpr int SIM_N = 200;           // number of nodes
inline constexpr int SIM_T = 200;           // number of time steps
inline constexpr int SIM_DEG_BINS = 31;     // degree histogram bins (0, 1, ..., 30+)
inline constexpr int SIM_N_REPLICATES = 40; // number of replicates per parameter set
inline constexpr double P_EDGE = 0.05;      // probability of edge in initial graph
inline constexpr int N_INFECTED_0 = 5;      // initial number of infected nodes

struct SimResult {
    std::vector<double> infected_fraction = std::vector<double>(SIM_T + 1, 0.0);
    std::vector<long long> rewire_counts = std::vector<long long>(SIM_T + 1, 0);
    std::vector<long long> degree_histogram = std::vector<long long>(SIM_DEG_BINS, 0);
};

enum class State : uint8_t {
    SUSCEPTIBLE = 0,
    INFECTED = 1,
    RECOVERED = 2
};