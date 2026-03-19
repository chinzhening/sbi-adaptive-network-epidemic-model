/**
 * @file simulator.hpp
 * @brief Adaptive-network SIR epidemic simulator.
 *
 * This module defines an SIR (Susceptible–Infected–Recovered) epidemic
 * model on a dynamically evolving network. Susceptible nodes may rewire
 * connections to avoid infected neighbors, coupling disease spread with
 * network topology.
 *
 * The simulation proceeds in discrete time steps:
 *   1. Infection
 *   2. Recovery
 *   3. Rewiring
 *
 * Reference:
 *   Gross et al. (2006), Physical Review Letters, 96(20), 208701.
 */
#pragma once
#include "common.hpp"
#include "summary.hpp"

SimResult simulate_one(
    double beta,
    double gamma,
    double rho,
    int seed
);

SummaryStatistics simulate_and_summarize(
    double beta,
    double gamma,
    double rho,
    const std::vector<StatIndex>& active_stats
);