# Simulator

The C++ simulator implements the adaptive-network SIR model and the ABC rejection sampler. It reads observed data and a configuration file, runs `n_simulations` parameter draws from the prior, computes summary statistics for each, and writes accepted samples to a timestamped output directory under `results/`.

---

## Building

```bash
./build.sh
```

This runs CMake in Release mode and produces the executable at `build/abc_sampler`. Requires a C++17 compiler (GCC ≥ 11 or Clang ≥ 14) and CMake ≥ 3.20. The build is parallelised automatically via `--parallel`.

---

## Running

```bash
./run.sh experiments/reference_table.toml
```

`run.sh` builds (if not already built) and then invokes `build/abc_sampler <config>`. Results are written to `results/<experiment_name>/<timestamp>/`. A `run_info.txt` file in the output directory records the exact output path.

To run with a custom config:

```bash
./run.sh path/to/my_config.toml
```

---

## Configuration format

Config files use TOML with four sections.

### `[experiment]`

| Field | Type | Description |
|---|---|---|
| `name` | string | Used as the output subdirectory name under `results/` |

### `[prior]`

Uniform prior bounds for each parameter.

| Field | Default | Description |
|---|---|---|
| `beta_min` / `beta_max` | 0.05 / 0.5 | Infection rate bounds |
| `gamma_min` / `gamma_max` | 0.02 / 0.2 | Recovery rate bounds |
| `rho_min` / `rho_max` | 0.0 / 0.8 | Rewiring rate bounds |

### `[abc]`

| Field | Type | Default | Description |
|---|---|---|---|
| `n_simulations` | int | 10000 | Total number of parameter draws |
| `acceptance_rate` | float | 0.01 | Fraction of simulations to accept (sets ε as the corresponding distance quantile) |
| `normalization` | string | `"None"` | Summary statistic normalisation: `"None"` or `"equalize_variance"` |
| `distance` | string | `"euclidean"` | Distance function: `"euclidean"` |
| `active_stats` | list of strings | — | Which summary statistics to use (see below) |

### `[io]`

Paths to the observed data files. These should point to `data/raw/`.

| Field | Description |
|---|---|
| `final_degree_histograms_path` | Final degree distribution per replicate |
| `infected_timeseries_path` | Infected fraction time series per replicate |
| `rewiring_timeseries_path` | Rewiring event count time series per replicate |

### Example configs

**`experiments/reference_table.toml`** — 100,000 simulations for building the reference table used in the Python analysis notebooks.

**`experiments/test_set.toml`** — 300 simulations for building the held-out test set used in SBC calibration.

---

## Available summary statistics

The following names are valid entries in `active_stats`:

| Name | Description |
|---|---|
| `peak_infected_fraction` | Maximum infected fraction over all time steps |
| `time_to_peak_infected_fraction` | Time step at which peak infection occurs |
| `auc_infected_fraction` | Discrete integral of infected fraction over time |
| `initial_growth_ratio` | Ratio of infected fraction at t=1 to t=0 |
| `total_rewire_count` | Total rewiring events across all time steps |
| `peak_rewire_count` | Maximum rewiring events in a single time step |
| `time_to_peak_rewire_count` | Time step at which peak rewiring occurs |
| `mean_degree` | Mean node degree in the final network |
| `sd_degree` | Standard deviation of node degrees in the final network |
| `lag_peak` | Signed difference between time to peak rewire and time to peak infection |
| `rewire_to_infection_ratio` | Total rewiring events divided by total new infections |

Statistics are computed per replicate and aggregated as mean and standard deviation across `R = 40` independent replicates before distance computation, yielding two columns per active statistic in the output.

---

## Output format

Results are written to `results/<experiment_name>/<timestamp>/` and contain:

**`abc_results.csv`** — one row per simulation (all `n_simulations`, not just accepted). Columns:

| Column | Description |
|---|---|
| `beta`, `gamma`, `rho` | Sampled parameter values |
| `mean:<stat>`, `sd:<stat>` | Aggregated summary statistics for each active stat |
| `distance` | Euclidean distance to observed summaries |
| `accepted` | Boolean — whether this row was accepted |

**`config.toml`** — copy of the config used for this run.

**`run_info.txt`** — metadata including output directory path and wall-clock runtime.