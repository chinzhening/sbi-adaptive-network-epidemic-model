# Reproducing all results

Run the notebooks in the order below. Each notebook writes outputs to `results/` and the paper figures are copied to `paper/figures/` manually (or are the same files).

**Prerequisites:** reference table and test set must exist at `data/sim/reference_table.csv` and `data/sim/test_set.csv`. See [data.md](data.md) if you need to regenerate them.

```bash
jupyter lab analysis/
```

---

## `analysis/01_preliminary.ipynb` → `results/preliminary/`

Report §2: Basic Rejection ABC.

| Output file | Report location |
|---|---|
| `base_marginal_posterior.png` | Figure 1 — marginal KDEs for all ε |
| `base_pairwise_joint.png` | Figure 2 — joint posterior at ε = 0.001 |
| `base_posterior_summary.csv` | Table 2 — posterior summaries |
| `base_posterior_samples.npy` | Used as input by `03_advanced.ipynb` |

Then run the posterior predictive check separately:

```bash
python -m analysis.posterior_predictive_check
```

| Output file | Report location |
|---|---|
| `posterior_predictive_check.png` | Figure 3 — posterior predictive check |
| `posterior_predictive_samples.csv` | — |

---

## `analysis/02_summary.ipynb` → `results/summary/`

Report §3: Summary Statistics Design.

| Output file | Report location |
|---|---|
| `results.csv` | Table 3 — simulation study metrics (RARMISE, RAE, KS) |
| `marginal_kdes.png` | Figure 4 (top) — marginal posteriors for all methods at ε = 0.01 |
| `rf_pairwise_joint.png` | Figure 4 (bottom) — rf joint posterior |
| `gb_pairwise_joint.png` | — |
| `rf_posterior_summary.csv` | Table 4 — rf posterior point estimates |
| `gb_posterior_summary.csv` | Table 4 — gb posterior point estimates |
| `rf_feature_importances.csv` | Table 5 — rf feature importance scores |
| `gb_feature_importances.csv` | — |
| `pls_component_scores.csv` | — |
| `rf_posterior_samples.npy` | Used as input by `03_advanced.ipynb` |
| `gb_posterior_samples.npy` | Used as input by `03_advanced.ipynb` |
| `all_posterior_samples.npy` | Used as input by `03_advanced.ipynb` |
| `pls_posterior_samples.npy` | — |

---

## `analysis/03_advanced.ipynb` → `results/advanced/`

Report §4: Advanced Methods (APT-MAF / NPE).

**Requires** `results/preliminary/base_posterior_samples.npy`, `results/summary/all_posterior_samples.npy`, `results/summary/rf_posterior_samples.npy`, and `results/summary/gb_posterior_samples.npy` to exist (i.e. run notebooks 01 and 02 first).

| Output file | Report location |
|---|---|
| `npe_posterior_samples.npy` | Source for all NPE posterior plots |
| `npe_pairwise_posterior.png` | — (sbi pairplot) |
| `npe_pairwise_joint.png` | Figure 6 — APT-MAF pairwise joint posterior |
| `npe_marginal_kdes.png` | — (NPE marginals only) |
| `npe_marginal_comparison.png` | Figure 5 — all methods marginal comparison |
| `npe_posterior_summary.csv` | Table 6 (point estimates) |
| `sbc_check_stats.csv` | Table 6 (C2ST and KS calibration statistics) |
| `sbc_rank_plot_hist.png` | Figure 7 — SBC rank histograms |

---

## Notes

- All notebooks write to `results/` first. Figures used in the paper are then present in both `results/` and `paper/figures/` — the paper directory contains the versions actually included in the Typst source.
- GPU is used automatically if available during `03_advanced.ipynb` (APT-MAF training). CPU fallback works but training takes significantly longer.
- Random seeds are fixed where possible (`random_state=3247`) but NPE training may show minor variation across runs due to GPU non-determinism.