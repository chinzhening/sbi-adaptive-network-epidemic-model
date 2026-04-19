/**
 * @file simulator.cpp
 * @brief Implementation of the adaptive-network SIR simulator.
 *
 * Contains internal helper functions and the implementation of the
 * simulation logic defined in simulator.hpp.
 */
#include "simulator.hpp"
#include <random>

/** Checks if nodes i and j are neighbors.
 */
inline bool is_neighbor(
    const std::vector<std::vector<int>>& neighbors,
    const std::vector<int>& degree,
    int i, int j
) {
    for (int k = 0; k < degree[i]; ++k) {
        if (neighbors[i][k] == j) return true;
    }
    return false;
}

/** Adds edge i-j. Note that this does not check if the edge already exists, so
 * be careful to avoid duplicates. We rely on the caller to ensure that degree
 * constraints are respected.
 */
inline void add_edge(
    std::vector<std::vector<int>>& neighbors,
    std::vector<int>& degree,
    int i, int j
) {
    neighbors[i][degree[i]++] = j;
    neighbors[j][degree[j]++] = i;
}

/** Removes edge i-j using swap-delete method. Note that this changes the order
 * of neighbors, but that's fine since we don't rely on any order.
 */
inline void remove_edge(
    std::vector<std::vector<int>>& neighbors,
    std::vector<int>& degree,
    int i, int j
) {
    for (int k = 0; k < degree[i]; ++k) {
        if (neighbors[i][k] == j) {
            neighbors[i][k] = neighbors[i][degree[i] - 1];
            degree[i]--;
            break;
        }
    }
    for (int k = 0; k < degree[j]; ++k) {
        if (neighbors[j][k] == i) {
            neighbors[j][k] = neighbors[j][degree[j] - 1];
            degree[j]--;
            break;
        }
    }
}

/** Run one replicate of the adaptive-network SIR model.
 */
SimResult simulate_one(
    double beta,
    double gamma,
    double rho,
    int seed
) {
    std::mt19937 rng(seed < 0
        ? std::random_device{}()
        : static_cast<uint32_t>(seed));
    std::uniform_real_distribution<double> uni(0.0, 1.0);
    std::uniform_int_distribution<int> node_dist(0, SIM_N - 1);

    /** STEP 0: Build the initial contact network as an Erdos-Renyi graph.
     *   
     *  We represent the network as an adjacency list, with fixed size vectors
     *  for each node to store neighbors. We also maintain a degree vector to
     *  keep track of how many neighbors each node has. This allows us to
     *  efficiently add and remove edges without needing to resize vectors
     *  or use linked lists.
     *  
     *  For each pair of nodes (i, j), we add an edge with probability p_edge.
     *  This produces an undirected graph.
    */
    std::vector<std::vector<int>> neighbors(SIM_N, std::vector<int>(SIM_N, -1));
    std::vector<int> degree(SIM_N, 0);
    
    for (int i = 0; i < SIM_N; ++i) {
        for (int j = i + 1; j < SIM_N; ++j) {
            if (uni(rng) < P_EDGE)
                add_edge(neighbors, degree, i, j);
        }
    }

    /** Initialize the health state of each node.
     * 
     *  We encode each state as integers:
     *    0 = susceptible (S): can catch the disease
     *    1 = infected    (I): currently infectious
     *    2 = recovered   (R): immune, cannot be infected again
     * 
     *  At t = 0, we pick n_infected_0 nodes to be infected.
     *  All other nodes start as susceptible.
    */
    std::vector<State> state(SIM_N, State::SUSCEPTIBLE);

    // Infect the first n_infected_0 nodes (arbitrary choice)
    for (int k = 0; k < N_INFECTED_0; ++k) {
        state[k] = State::INFECTED;
    }

    // Output vectors
    std::vector<double> infected_fraction(SIM_T + 1);
    std::vector<long long> rewire_counts(SIM_T + 1, 0);

    auto count_infected = [&]() {
        int cnt = 0;
        for (int i = 0; i < SIM_N; ++i)
            if (state[i] == State::INFECTED) cnt++;
        return (double)cnt / SIM_N;
    };

    infected_fraction[0] = count_infected();

    /** Main Simulation Loop: iterate over SIM_T discrete time steps.
     *  Each time step has three phases applied in order:
     *    Phase 1: Infection (S -> I transitions)
     *    Phase 2: Recovery (I -> R transitions)
     *    Phase 3: Rewiring (network topology changes)
     */
    for (int t = 1; t <= SIM_T; ++t) {

        // Phase 1: Infection (synchronous update)
        std::vector<int> new_inf;

        for (int i = 0; i < SIM_N; ++i) {
            if (state[i] != State::INFECTED) continue;

            for (int k = 0; k < degree[i]; ++k) {
                int j = neighbors[i][k];
                if (state[j] == State::SUSCEPTIBLE && uni(rng) < beta) {
                    new_inf.push_back(j);
                }
            }
        }

        // Phase 2: Recovery
        for (int i = 0; i < SIM_N; ++i) {
            if (state[i] == State::INFECTED && uni(rng) < gamma) {
                state[i] = State::RECOVERED;
            }
        }

        // Apply all new infections at once.
        for (int j : new_inf) state[j] = State::INFECTED;

        // Phase 3: Rewiring (adaptive behaviour)
        long long rewire_count = 0;

        for (int s = 0; s < SIM_N; ++s) {
            if (state[s] != State::SUSCEPTIBLE) continue;

            int k = 0;
            while (k < degree[s]) {
                int i_node = neighbors[s][k];

                if (state[i_node] != State::INFECTED) {
                    k++;
                    continue;
                }

                if (uni(rng) >= rho) {
                    k++;
                    continue;
                }

                // Remove edge
                remove_edge(neighbors, degree, s, i_node);

                // Find new neighbor
                std::vector<int> candidates;
                for (int i = 0; i < SIM_N; ++i) {
                    if (i != s && !is_neighbor(neighbors, degree, s, i)) {
                        candidates.push_back(i);
                    }
                }

                // If there are no candidates, we cannot rewire, so skip.
                if (candidates.empty()) {
                    k++;
                    continue;
                }

                std::uniform_int_distribution<int> candidate_dist(0, candidates.size() - 1);
                int new_partner = candidates[candidate_dist(rng)];
                add_edge(neighbors, degree, s, new_partner);
                rewire_count++;
            }
        }

        infected_fraction[t] = count_infected();
        rewire_counts[t] = rewire_count;
    }

    /** Compute the degree histogram at the final time step.
     * 
     *  The degree of a node is its number of connections (neighbors).
     *  We bin degrees from 0 to 29 individually, and lump all degrees >= 30
     *  into a single bin (index 30). This gives a fixed-size output array
     *  of shape (31,) regardless of the actual degree distribution.
     */
    std::vector<long long> degree_histogram(31, 0);

    for (int i = 0; i < SIM_N; ++i) {
        int d = std::min(degree[i], 30);
        degree_histogram[d]++;
    }

    return {infected_fraction, rewire_counts, degree_histogram};
}


DenseStats simulate_and_summarize(
    double beta,
    double gamma,
    double rho,
    const StatLayout& layout
) {
    std::vector<DenseStats> all_stats(SIM_N_REPLICATES);
    for (int j = 0; j < SIM_N_REPLICATES; ++j) {
        SimResult result = simulate_one(beta, gamma, rho, -1);
        all_stats[j] = compute_summary_statistics(result, layout);
    }
    return aggregate_summary_statistics(all_stats, layout);
}