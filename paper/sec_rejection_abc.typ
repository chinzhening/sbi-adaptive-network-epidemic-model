#import "template.typ":*

#part("Basic Rejection ABC")

We begin with basic rejection ABC with few summary statistics as a baseline for
inference on $(beta, gamma, rho)$. \
 \
*Algorithm 1*
#enum(
  numbering: "1.",
  [Calculate summary statistics $s = S(D)$ from observed data],
  [For $t = 1$ to $t = N$,
  #enum(
    numbering: "i.",
    [Sample $theta'_t$ from the prior distribution $p(theta)$],
    [Simulate data $D'_t '$ from the model, $p(D|theta'_t)$],
    [Calculate summary statistics $s'_t = S(D'_t)$ from simulated data.],
  )
  ],
  [Scale $s$ and $s'_t$ for $t = 1$ to $t = N$ appropriately (e.g. mean zero and unit variance).],
  [For $t = 1$ to $t = N$, calculate distance and accept $d_t = d(s, s'_t) <= delta_epsilon$, with the scaled summaries.],
  [Estimate posterior density $p(theta|s)$ from the $epsilon N$ accepted parameters $theta'_t$.],
) \
As $epsilon -> 0$, the approximate posterior density $p(theta|s)$ converges to the true posterior $p(theta|D)$, but the acceptance rate becomes very low, leading to high computational cost. In practice, we choose a small but non-zero $epsilon$ to balance accuracy and efficiency.

== Setup
We performed $N = 10^5$ simulations, drawing parameters independently
from the prior at each iteration. For each draw, $R = 40$ independent
replicates were simulated and a vector of summary statistics was computed and
averaged across replicates. The statistics capture epidemic dynamics — area
under the infected fraction curve, peak infected fraction, and time to peak
infection — as well as network restructuring: total and peak rewiring counts,
time to peak rewiring, and the mean and standard deviation of the final degree
distribution. The choice of these summary statistics is somewhat arbitrary, but they were
chosen to capture key features that are likely to be informative about the
parameters.
Acceptance was based on the Euclidean distance between observed and simulated
summary vectors, with acceptance rate $epsilon in {0.1, 0.01, 0.001}$. 
Full descriptions and motivation for the summary statistics are provided in
@appendix:a (see @summary_stats_desc).

== Results
Overall, the rejection ABC results indicate that the parameters are identifiable
from the chosen summary statistics, as shown by the strong contraction of the
posteriors relative to the priors across all $epsilon$ thresholds and the stability
of posterior summaries under decreasing tolerance (see @preliminary:base_marginals).
The joint posterior reveals strong positive dependence between $beta$ and $rho$,
see @preliminary:base_pairwise_joint,
characterised by a narrow ridge of high posterior density, while $gamma$ appears
more weakly constrainted.
This suggests partial non-identifiability due to structural confounding, since both
parameters similarly affect early epidemic growth and peak dynamics and can
therefore compensate for one another.

#show figure: set text(size: 9pt)
#figure(
  caption: [Posterior summaries of parameters from basic rejection ABC for $epsilon in {0.1, 0.01, 0.001}$],
)[
  #table(
    columns: 6,
    align: center,
    inset: (y: 4pt, x: 6pt),
    [$epsilon$], [Parameter], [Mode], [Mean], [Median], [95% HDP],
    
    table.cell(rowspan: 3)[0.1],
    [$beta$],  [0.1699], [0.2181], [0.2055], [(0.0753, 0.3849)],
    [$gamma$], [0.1020], [0.1261], [0.1254], [(0.0606, 0.2000)],
    [$rho$],   [0.2826], [0.2578], [0.2635], [(0.0368, 0.4637)],
    
    table.cell(rowspan: 3)[0.01],
    [$beta$],  [0.1563], [0.1535], [0.1529], [(0.0981, 0.2129)],
    [$gamma$], [0.0990], [0.1174], [0.1126], [(0.0615, 0.1804)],
    [$rho$],   [0.2689], [0.2545], [0.2573], [(0.1273, 0.3857)],
    
    table.cell(rowspan: 3)[0.001],
    [$beta$],  [0.1304], [0.1376], [0.1347], [(0.1066, 0.1718)],
    [$gamma$], [0.0987], [0.1008], [0.1000], [(0.0715, 0.1268)],
    [$rho$],   [0.2440], [0.2473], [0.2464], [(0.1786, 0.3155)],
  )
] <preliminary:base_posterior_summaries>

#figure(
  caption: "Posterior marginal distributions of parameters from rejection ABC with KDE.",
)[
  #image(
    "figures/preliminary/base_marginal_posterior.png",
    alt: "Posterior distributions of parameters from the rejection ABC experiment with KDE and credible intervals",
  )
] <preliminary:base_marginals>

#figure(
  caption: [Joint posterior distributions of parameters from rejection ABC for $epsilon = 0.001$],
)[
  #image(
    "figures/preliminary/base_pairwise_joint.png",
    alt: "Joint posterior distributions of parameters from rejection ABC for $epsilon = 0.001$",
  )
] <preliminary:base_pairwise_joint>

// 4. Posterior validation and diagnostics
== Validation
Posterior predictive checks were performed by simulating data from the accepted parameters and comparing the resulting summary statistics to those of the observed data (see //@preliminary:base_ppc).
The posterior predictive distributions of the summary statistics capture the observed
values well, but the variability across simulations is large.

#figure(
  caption: [Posterior predictive check comparing observed summary statistics to those from simulations using accepted parameters from rejection ABC with $epsilon = 0.01$],
)[
  #image(
    "figures/preliminary/posterior_predictive_check.png",
    alt: "Posterior predictive check comparing observed summary statistics to those from simulations using accepted parameters from rejection ABC with $epsilon = 0.01$",
  )
] <preliminary:base_ppc>

#pagebreak()