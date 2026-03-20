#include <iostream>
#include <filesystem>

#include "config.hpp"
#include "io.hpp"
#include "simulator.hpp"
#include "summary.hpp"

void print_usage() {
    std::cerr << "Usage: simulate --beta B --gamma G --rho R "
              << "--stats S1 S2 S3 [--n_sim N] [--output dir]\n";
}

int main(int argc, char* argv[]) {
    double beta = -1, gamma = -1, rho = -1;
    std::vector<std::string> stat_names;
    std::string output_dir  = "";
    int n_sim = 1000;

    // parse CLI args
    for (int i = 1; i < argc - 1; ++i) {
        std::string arg = argv[i];
        if      (arg == "--beta")   beta        = std::stod(argv[i + 1]);
        else if (arg == "--gamma")  gamma       = std::stod(argv[i + 1]);
        else if (arg == "--rho")    rho         = std::stod(argv[i + 1]);
        else if (arg == "--n_sim")  n_sim       = std::stoi(argv[i + 1]);
        else if (arg == "--output") output_dir  = argv[i + 1];
        else if (arg == "--stats") {
            // collect all following values until the next flag (starts with --)
            for (int j = i + 1; j < argc; ++j) {
                std::string val = argv[j];
                if (val.rfind("--", 0) == 0) break;  // stop at next flag
                stat_names.push_back(val);
            }
        }
    }

    if (beta < 0 || gamma < 0 || rho < 0) {
        print_usage();
        return 1;
    }

    // try to parse stat name
    if (stat_names.empty()) {
        std::cerr << "Error: at least one --stats value required\n";
        print_usage();
        return 1;
    }

std::vector<StatIndex> active_stats;
for (const auto& name : stat_names)
    active_stats.push_back(stat_id_from_string(name));

    // create output directory if it doesn't exist
    std::filesystem::path out = std::filesystem::path(output_dir);
    std::filesystem::create_directories(out);

    std::vector<SummaryStatistics> s_sim(n_sim);
    
    // run ensemble
    #pragma omp parallel for
    for (int i = 0; i < n_sim; ++i) {
        s_sim[i] = simulate_and_summarize(beta, gamma, rho, active_stats);
    }

    // save results
    save_simulation_results(s_sim, active_stats, out);

    std::cout << "Output directory: " << out << "\n";
    return 0;
    
}