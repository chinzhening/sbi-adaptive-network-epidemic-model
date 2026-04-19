#include "config.hpp"

#include <toml++/toml.hpp>
#include <stdexcept>

#include <iostream>

Normalization parse_normalization(const std::string& s) {
    if (s == "equalize_variance") return Normalization::EQUALIZE_VARIANCE;
    if (s == "equalize_mad")      return Normalization::EQUALIZE_MAD;
    if (s == "None")              return Normalization::NONE;
    throw std::invalid_argument("Unknown normalization: " + s);
}

DistanceFunction parse_distance(const std::string& s) {
    if (s == "euclidean") return DistanceFunction::EUCLIDEAN;
    throw std::invalid_argument("Unknown distance: " + s);
}

StatIndex stat_id_from_string(const std::string& s) {
    for (int i = 0; i < N_STATS; ++i) {
        if (s == STAT_NAMES[i]) {
            return static_cast<StatIndex>(i);
        }
    }
    throw std::invalid_argument("Unknown statistic: " + s);
}

Config load_config(const std::string& path) {
    auto tbl = toml::parse_file(path);
    Config cfg;

    // Experiment
    cfg.experiment.name = tbl["experiment"]["name"].value_or(std::string("experiment"));

    // prior
    cfg.prior.beta_min  = tbl["prior"]["beta_min"].value_or(0.05);
    cfg.prior.beta_max  = tbl["prior"]["beta_max"].value_or(0.5);
    cfg.prior.gamma_min = tbl["prior"]["gamma_min"].value_or(0.02);
    cfg.prior.gamma_max = tbl["prior"]["gamma_max"].value_or(0.2);
    cfg.prior.rho_min   = tbl["prior"]["rho_min"].value_or(0.0);
    cfg.prior.rho_max   = tbl["prior"]["rho_max"].value_or(0.8);

    // abc
    cfg.abc.n_simulations   = tbl["abc"]["n_simulations"].value_or(10000);
    cfg.abc.epsilon         = tbl["abc"]["epsilon"].value_or(-1.0);
    cfg.abc.acceptance_rate = tbl["abc"]["acceptance_rate"].value_or(-1.0);

    // Determine which criterion to use
    if (cfg.abc.epsilon > 0.0) {
        cfg.abc.use_epsilon = true;
    } else if (cfg.abc.acceptance_rate > 0.0 && cfg.abc.acceptance_rate <= 1.0) {
        cfg.abc.use_epsilon = false;
    } else {
        // Neither epsilon nor acceptance_rate properly set, use a default
        cfg.abc.epsilon = 1.0;
        cfg.abc.use_epsilon = true;
    }

    if (auto s = tbl["abc"]["normalization"].value<std::string>())
        cfg.abc.normalization = parse_normalization(*s);

    if (auto s = tbl["abc"]["distance"].value<std::string>())
        cfg.abc.distance = parse_distance(*s);

    if (auto arr = tbl["abc"]["active_stats"].as_array())
        for (const auto& el : *arr)
            if (auto s = el.value<std::string>())
                cfg.abc.active_stats.push_back(stat_id_from_string(*s));

    // io
    cfg.io.final_degree_histograms_path = tbl["io"]["final_degree_histograms_path"].value_or(
        std::string("data/final_degree_histograms.csv"));
    cfg.io.infected_timeseries_path = tbl["io"]["infected_timeseries_path"].value_or(
        std::string("data/infected_timeseries.csv"));
    cfg.io.rewiring_timeseries_path = tbl["io"]["rewiring_timeseries_path"].value_or(
        std::string("data/rewiring_timeseries.csv"));

    return cfg;
}