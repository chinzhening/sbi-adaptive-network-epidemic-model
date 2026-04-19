#import "template.typ":*

#part("Advanced Methods") <advanced_methods>

== Neural Posterior Estimation
While the semi-automatic ABC framework constructs summary statistics via
regression-based dimension reduction, the rejection step remains
computationally wasteful: the vast majority of simulations are discarded, and
inference must be repeated from scratch for each new observation. Neural
Posterior Estimation (NPE) addresses both limitations by training a neural
density estimator to directly approximate $p(theta|s)$ from simulated
$(theta, s)$ pairs, producing an amortised posterior that can be evaluated at
any observation without retraining.

NPE parametrises the posterior using a normalising flow, a composition of
invertible, differentiable transformations that maps a simple base distribution
(typically Gaussian) to a flexible target density. Because the transformations
are invertible, both sampling and exact density evaluation are tractable, and
the flow parameters are learned by maximum likelihood on simulated
$(theta, s)$ pairs. This allows the model to represent complex, multimodal,
and correlated posteriors that are out of reach for Gaussian or rejection-based
approximations.

=== Setup
We model the posterior using a Masked Autoregressive Flow (MAF)
#cite(<papamakarios2017maf>), in which each transformation is an autoregressive
network that conditions each output dimension on all previous ones, enabling
expressive density estimation while preserving tractable likelihoods. The flow
is fitted via Automatic Posterior Transformation (APT)
#cite(<greenberg2019apt>), as implemented in the `sbi` library
#cite(<tejero-cantero2020sbi>). APT trains the flow by maximising the
probability of simulated parameters under a dynamically updated proposal,
avoiding the importance weights and post-hoc corrections that destabilise
earlier sequential NPE approaches.

Training used $N = 10^4$ parameter–summary pairs drawn from the
reference table, with the full summary vector of size 22 as input.
No hyperparameter tuning was performed, and the default MAF architecture of 5
autoregressive layers with 50 hidden units each was used throughout, converging
after 211 epochs (#sym.tilde 2 minutes).

APT-MAF has been demonstrated on inputs of dimension $10^4$ without any summary
statistic construction #cite(<greenberg2019apt>), so its possible to use the raw
time series and final degree histogram as inputs. This may allow the model to
learn more informative features than the hand-crafted summaries, but will incur
greater computational cost. As we will see, the current setup already achieves
good performance with a fraction of the simulation budget required by ABC.

=== Posterior inference
The posterior was evaluated by drawing $n = 10^3$ samples from the fitted
density estimator conditioned on $s_"obs"$, requiring no rejection step or
tolerance threshold. Marginal posteriors for all methods except pls are shown in
@npe_marginal_comparison. APT-MAF closely follows the `rf` in the marginal posterior
shape for $gamma$, but the mode sits slightly higher. Compared to `rf`, APT-MAF
gives lower estimates of $beta$ and higher estimates of $rho$, with more
concentrated marginals.

#figure(
  caption: [Marginal posteriors for $beta$, $gamma$, and $rho$ under basic
  rejection ABC, `all`, `rf`, `gb` and `APT-MAF`.],
)[
  #image("figures/advanced/npe_marginal_comparison.png")
] <npe_marginal_comparison>

#figure(
  caption: [Pairwise joint posterior from APT-MAF, constructed from $n=1000$ samples.],
)[
  #image("figures/advanced/npe_pairwise_joint.png")
]

The number of simulation pairs used to train the NPE is much less than basic
rejection ABC and its variants e.g. ABC-SMC. These methods may have smaller
per-round compute budgets, but may still require large total simulation counts
to reach small tolerances #cite(<sisson2007smc>).

=== Calibration
Calibration was assessed via simulation-based calibration (SBC)
#cite(<talts2018sbc>) on 100 held-out parameter–summary pairs, drawing
$n = 10^3$ posterior samples per observation. We report the KS statistic
against uniformity of ranks, the Classifier Two-Sample Test (C2ST), a
binary classifier accuracy near 0.5 indicates the posterior and reference
samples are indistinguishable and the Data-Averaged Posterior (DAP)
statistic as a complementary coverage measure.

#figure(
  caption: [SBC rank histograms for $beta$, $gamma$, $rho$. Dashed line
  indicates perfect calibration.],
)[
  #image(
    "figures/advanced/sbc_rank_plot_hist.png",
    width: 85%,
  )
] <fig:sbc_hist>

The rank histograms (@fig:sbc_hist) are broadly uniform across all three
parameters, and all KS $p$-values sit comfortable above the significance level.
The C2ST statistics deviate little from 0.5, indicating no detectable
systematic bias in the learned posterior. This compares favourably to rejection ABC, where
coverage $p$-values were near zero for most parameter–method combinations, and
is broadly competitive with `rf`. However, the DAP statistic is somewhat on the
low side for all three parameters. This could be an artifact of the relatively
small number of posterior samples and calibration observations.

#figure(
  caption: [APT-MAF posterior estimates and SBC calibration statistics.],
)[
  #table(
    columns: 8,
    inset: (y: 4pt, x: 6pt),
    align: (left, center, center, center, center, center, center, center),
    [Parameter], [Mode], [Mean], [Median], [95% HPD interval],
    [KS#sub[100] Cov. $P$], [C2ST ranks], [C2ST DAP],
    [$beta$], [0.1322], [0.1315], [0.1316], [(0.1254, 0.1385)], [0.2527], [0.42], [0.39],
    [$gamma$], [0.0879], [0.0880], [0.0880], [(0.0862, 0.0896)], [0.1577], [0.545], [0.37],
    [$rho$],   [0.2443], [0.2445], [0.2446], [(0.2362, 0.2524)], [0.7511], [0.51], [0.33],
  )
] <fig:sbc_table>

Overall, APT-MAF achieves well-calibrated, concentrated posteriors for all
three parameters using a fraction of the simulation budget required by
rejection-based methods, and without explicit summary statistic construction
or tolerance selection. The results suggest that neural posterior estimation
is a viable and efficient alternative to ABC for this class of adaptive-network
models. Compared to semi-automatic ABC, NPE methods are easily scalable to
high-dimensional inputs such as time series.

#pagebreak()