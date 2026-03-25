#include <fstream>
#include <iostream>

#include "io.hpp"
#include "summary.hpp"
#include "rejection.hpp"

int main(int argc, char* argv[]) {
    // load config - path from CLI arg or default
    const std::string config_path = (argc > 1) ? std::string(argv[1]) : "config.toml";
    auto cfg = load_config(config_path);

    // create output directory if it doesn't exist
    std::filesystem::path output_dir = create_output_dir(cfg.experiment);

    // save a copy of the config for reproducibility
    std::filesystem::copy_file(config_path, output_dir / "config.toml");

    // load observed data
    auto data_obs = load_observed_data(cfg.io);

    // Create StatLayout for active summary statistics
    StatLayout layout = StatLayout { cfg.abc.active_stats };

    // compute observed summary statistics
    auto s_obs_vec = compute_summary_statistics(data_obs, layout);
    auto s_obs = aggregate_summary_statistics(s_obs_vec, layout);

    // run ABC rejection sampling
    ABCResult result = run_abc_rejection(cfg, s_obs, layout);

    std::cout << "Acceptance rate: " << result.acceptance_rate * 100.0 << "%" << std::endl;
    std::cout << "Elapsed time: " << result.runtime_seconds << " s" << std::endl;
    std::cout << "Average time per sample: " << result.runtime_seconds / cfg.abc.n_simulations << " s" << std::endl;

    // Store all results
    save_results(
        result.beta,
        result.gamma,
        result.rho,
        result.stats,
        layout,
        result.distances,
        result.accepted,
        output_dir
    );

    std::ofstream info(output_dir / "run_info.txt");
    info << "output_dir=" << output_dir.string() << "\n";
}