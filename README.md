# Simulation-Based Inference for an Adaptive-Network Epidemic Model

> Reproduction code for *Simulation-Based Inference For An Adaptive-Network Epidemic Model* (ST3247, NUS, 2026).

Approximate Bayesian Computation (ABC) and Neural Posterior Estimation (NPE) are applied to infer the infection rate β, recovery rate γ, and rewiring rate ρ of an adaptive-network SIR model from partially observed epidemic realisations.

---

## Repository structure

```
.
├── src/                    # C++ simulator source
├── include/                # C++ headers
├── experiments/            # Simulator config files (.toml)
├── analysis/               # Python analysis notebooks
│   ├── 01_preliminary.ipynb   # §2 Basic rejection ABC
│   ├── 02_summary.ipynb       # §3 Summary statistics design
│   └── 03_advanced.ipynb      # §4 NPE (APT-MAF)
├── data/
│   ├── raw/                # Observed time series and degree histograms
│   └── sim/                # Reference table and test set (gitignored)
├── results/                # Output figures, posteriors, and CSVs
├── paper/                  # Typst source for the report
├── docs/                   # Documentation
├── CMakeLists.txt
├── build.sh                # C++ build script
├── run.sh                  # Simulation run script
├── pyproject.toml
└── requirements.txt
```

---

## Quickstart

### 1. Build the C++ simulator

```bash
./build.sh
```

Requires a C++17 compiler (GCC ≥ 11 or Clang ≥ 14) and CMake ≥ 3.20.

### 2. Generate simulations

```bash
# Reference table (N = 10^5, ~25 min on a modern CPU)
./run.sh experiments/reference_table.toml

# Test set for calibration
./run.sh experiments/test_set.toml
```

Output CSVs are written to `results/` with a timestamped subdirectory. Copy the relevant files to `data/sim/` before running the notebooks.

### 3. Install Python dependencies

```bash
pip install .
# or, if using uv:
uv sync
```

### 4. Run the analysis notebooks

Run in order:

```bash
jupyter lab analysis/
```

| Notebook | Report section | Key outputs |
|---|---|---|
| `preliminary.ipynb` | §2 Basic rejection ABC | `results/preliminary/` |
| `summary.ipynb` | §3 Summary statistics | `results/summary/` |
| `advanced.ipynb` | §4 NPE | `results/advanced/` |

---

## Requirements

- Python ≥ 3.10
- C++17 compiler
- CMake ≥ 3.20
- GPU recommended for NPE training (CPU fallback works but is slow)
- See `requirements.txt` for Python packages

---

## Docs

| File | Contents |
|---|---|
| `docs/simulator.md` | Config file format, CLI flags, parallelism, output schema |
| `docs/data.md` | Reference table and test set schema; how to download precomputed files |
| `docs/reproduce.md` | Exact steps to reproduce every figure and table in the report |

