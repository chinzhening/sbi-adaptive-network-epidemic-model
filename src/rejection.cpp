#include <random>
#include <omp.h>

#include "distance.hpp"
#include "normalization.hpp"
#include "rejection.hpp"
#include "simulator.hpp"
#include "summary.hpp"


ABCResult run_abc_rejection(const Config& cfg, const SummaryStatistics& s_obs) {
    ABCResult result;

    std::mt19937 rng(42); // fixed seed for reproducibility

    std::vector<double> beta(cfg.abc.n_simulations);
    std::vector<double> gamma(cfg.abc.n_simulations);
    std::vector<double> rho(cfg.abc.n_simulations);

    // Priors for beta, gamma, rho
    std::uniform_real_distribution<double> dist_beta(cfg.prior.beta_min, cfg.prior.beta_max);
    std::uniform_real_distribution<double> dist_gamma(cfg.prior.gamma_min, cfg.prior.gamma_max);
    std::uniform_real_distribution<double> dist_rho(cfg.prior.rho_min, cfg.prior.rho_max);

    const int n_samples = cfg.abc.n_simulations;

    for (int i = 0; i < n_samples; ++i) {
        beta[i] = dist_beta(rng);
        gamma[i] = dist_gamma(rng);
        rho[i] = dist_rho(rng);

    }

    // store the stats for all samples in a vector of SummaryStatistics
    std::vector<SummaryStatistics> s_sim(n_samples);

    double start = omp_get_wtime();
    #pragma omp parallel for
    for (int i = 0; i < n_samples; ++i) {
        s_sim[i] = simulate_and_summarize(
            beta[i],
            gamma[i],
            rho[i],
            cfg.abc.active_stats
        );
    }
    double end = omp_get_wtime();
    result.runtime_seconds = end - start;

    // normalize
    std::vector<double> norm_scale = compute_normalization_scale(s_sim, cfg.abc.normalization, cfg.abc.active_stats);
    std::vector<SummaryStatistics> s_sim_norm = apply_scaling(s_sim, norm_scale, cfg.abc.active_stats);
    SummaryStatistics s_obs_norm = apply_scaling(s_obs, norm_scale, cfg.abc.active_stats);

    // compute distances
    std::vector<double> distances(n_samples);
    std::vector<bool> accepted(n_samples);
    int n_accepted = 0;

    for (int i = 0; i < n_samples; ++i) {
        distances[i] = compute_distance(s_sim_norm[i], s_obs_norm, cfg.abc.distance);
        accepted[i] = distances[i] <= cfg.abc.epsilon;
        if (accepted[i])
            n_accepted++;
    }

    double acceptance_rate = static_cast<double>(n_accepted) / cfg.abc.n_simulations;

    return ABCResult {
        beta,
        gamma,
        rho,
        s_sim_norm,
        distances,
        accepted,
        acceptance_rate,
        cfg.abc.epsilon,
        result.runtime_seconds
    };
}