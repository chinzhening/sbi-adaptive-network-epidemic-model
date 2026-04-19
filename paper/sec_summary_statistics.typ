#import "template.typ":*

#part("Summary Statistics Design") <summary_statistics>

The performance of ABC inference depends critically on the choice of summary statistics.
In our setting, the relationship between the parameters and the observable data
involves feedback between the epidemic dynamics and the network rewiring, making
it difficult to identify informative summary statistic sets a priori.
Using too many summary statistics can also degrade performance due to the curse
of dimensionality, whereas using too few may lead to loss of information and biased
inference.

To address this, we adopt a data-driven approach and consider two methods from
the literature: (1) Partial least squares (PLS) regression and (2)
regression-based summary construction. PLS constructs
linear combinations of the candidate summaries that are maximally
decorrelated and are also are highly correlated with the parameters
#cite(<wegmann_efficient_2009>). A reduction is achieved by selecting the top
$r$ components, where $r$ is chosen via cross-validation, minimizing the root
mean squared error of prediction (RMSEP). For regression-based summary
construction, we follow the semi-automatic ABC framework of
#cite(<fearnhead2012semiabc>), who establish that the theoretically optimal
summary statistics are the posterior means of the parameters. While these cannot
be computed analytically, they can be estimated from simulated $(theta, s)$ pairs,
and the resulting estimates used as summary statistics within ABC. We approximate
the posterior mean function using a random forest #cite(<10.1093.bioinformatics.bty867>)
and a gradient boosting model, both fitted to the training simulations; the
out-of-sample predicted parameter values then serve as the transformed summary
statistics passed to the rejection and regression adjustment steps.

== Simulation Study
To assess the performance of these methods and the effect of the acceptance
threshold $epsilon$, we conduct a simulation study. For each
$epsilon in {0.001, 0.01, 0.1}$, we generate 100 datasets with parameter values
sampled from the prior distributionand perform ABC inference for each dataset.

=== Methods
#enum(
  indent: 0.5em,
  [*Candidate Summary Statistics.* We construct a set of candidate statistics
  designed to capture both epidemic dynamics and adaptive network behaviour. For
  each simulation, we compute across the replicates the mean and standard
  deviation of the following features: peak infected fraction, time to peak
  infection, area under the infection curve, initial growth rate, total rewire
  count, peak rewire count, time to peak rewire count, the ratio of rewiring to
  infection, the lag between the infection and rewiring peaks, and the mean
  and standard deviation of the final degree distribution. This amounts to a total
  of 22 candidate summary statistics.],

  [*Implementation.* All simulations and inference procedures use the prior
   described in @model_parameters_desc. For the ABC rejection algorithm, we
   performed $N = 10^5$ simulations and stored these in a reference table. In
   the summary statistic selection step, we used $n=10^4$ simulations drawn
   without replacement from the reference table. Post-rejection adjustment was
   performed by default via weighted local-linear regression with weights from
   an Epanechnikov kernel, following #cite(<Beaumont2002-ax>), without
   additional scaling of the parameters.
  #enum(
    numbering: "(a)",
    indent: 0.15em,
    [For the PLS method, we used the `PLSRegression` model from the `scikit-learn`
    library (Pedregosa et al. 2011) and followed Wegmann et al. (2009). Instead
    of a Box-Cox transformation, we applied a Yeo–Johnson power transformation
    followed by standardisation to zero mean and unit variance to the summary
    statistics prior to fitting the PLS regression model. This is because the
    Yeo–Johnson transformation does not require strictly positive inputs. The
    number of components to retain was chosen by 10-fold cross-validation based
    on the root mean squared error of prediction over a grid of up to 22
    components; this procedure selected $r = 5$ components for `pls`. At
    inference time, the fitted PLS projection was applied to transform the
    observed and accepted summary statistics prior to distance computation and
    regression adjustment.],

    [For the random forest method, we fitted one `RandomForestRegressor` model
    per parameter, each consisting of 100 regression trees, to the training
    statistics and parameter values. The fitted ensemble was then used to predict
    parameter values from summary statistics, and the resulting predicted values
    served as the transformed summary statistics passed to the rejection and
    adjustment steps. This construction implicitly performs a nonlinear,
    parameter-specific dimension reduction by mapping the high-dimensional
    summary vector to a scalar prediction for each parameter.],

    [For the gradient boosting method, we proceeded analogously, fitting one
    `GradientBoostingRegressor` model per parameter with 100 boosting stages.
    As with the random forest approach, the predicted parameter values from the
    fitted ensemble were used as transformed summaries.]
  )
  Both ensemble methods were implemented using the `scikit-learn` library, with
  all remaining hyperparameters set to their defaults. Standardization to mean zero
  and unit variance was applied to the summaries after transformation by
  the fitted ensemble.],

  [*Evaluation metrics.* To assess estimation accuracy and posterior calibration,
  we report four metrics across 100 simulations. The relative absolute error of
  the mean integrated squared error (RAEMISE) measures the overall accuracy of
  the estimated posterior density relative to a baseline. The relative absolute
  error (RAE) of the posterior mode, mean, and median each measure point
  estimation accuracy for the corresponding summary of the posterior. Finally,
  posterior calibration is assessed via the Kolmogorov--Smirnov (KS) statistic,
  alongside the associated coverage $p$-value; a
  uniform distribution of posterior probabilities of the true parameter value is
  expected under a well-calibrated posterior, and significant deviations from
  uniformity indicate systematic bias or miscoverage.]
) \

#show figure: set text(size: 9pt, font: fonts.sans_serif) 
#figure(
  gap: 1em,
  caption: [
    Accuracy of different methods for choosing summary statistics on a global scale.],
)[
  #table(
    columns: 9,
    align: (left, center, center, center, center, center, center, center, left),
    inset: (y: 4pt, x: 6pt),
    [Method], [$epsilon$], [Parameter], [RARMISE#super[a]], [RAE mean], [RAE#super[b] mode], [RAE median], [KS#sub[100]#super[c]], [Cov. $P$],

    table.cell(rowspan: 9)[all.],
    table.cell(rowspan: 3)[0.1],
    [$beta$],  [0.063 (0.039)], [0.036 (0.036)], [0.034 (0.030)], [0.035 (0.035)], [0.137], [0.042\*],
    [$gamma$], [0.125 (0.117)], [0.049 (0.056)], [0.043 (0.054)], [0.045 (0.054)], [0.203], [0.000\*],
    [$rho$],   [0.156 (0.967)], [0.077 (0.461)], [0.078 (0.468)], [0.078 (0.471)], [0.109], [0.174],

    table.cell(rowspan: 3)[0.01],
    [$beta$],  [0.046 (0.026)], [0.028 (0.026)], [0.028 (0.026)], [0.027 (0.025)], [0.263], [0.000\*],
    [$gamma$], [0.074 (0.074)], [0.035 (0.035)], [0.035 (0.035)], [0.033 (0.033)], [0.209], [0.000\*],
    [$rho$],   [0.032 (0.040)], [0.015 (0.019)], [0.015 (0.019)], [0.015 (0.018)], [0.168], [0.006\*],

    table.cell(rowspan: 3)[0.001],
    [$beta$],  [0.039 (0.026)], [0.025 (0.025)], [0.025 (0.025)], [0.025 (0.025)], [0.233], [0.000\*],
    [$gamma$], [0.060 (0.061)], [0.037 (0.048)], [0.037 (0.048)], [0.036 (0.049)], [0.234], [0.000\*],
    [$rho$],   [0.019 (0.014)], [0.012 (0.010)], [0.012 (0.010)], [0.011 (0.010)], [0.175], [0.004\*],

    table.cell(rowspan: 9)[pls],
    table.cell(rowspan: 3)[0.1],
    [$beta$],  [0.111 (0.070)], [0.065 (0.059)], [0.056 (0.049)], [0.061 (0.056)], [0.189], [0.001\*],
    [$gamma$], [0.151 (0.128)], [0.071 (0.067)], [0.068 (0.070)], [0.068 (0.065)], [0.207], [0.000\*],
    [$rho$],   [1.019 (8.411)], [0.805 (7.399)], [1.096 (10.000)], [0.939 (8.634)], [0.076], [0.579],

    table.cell(rowspan: 3)[0.01],
    [$beta$],  [0.083 (0.045)], [0.052 (0.045)], [0.052 (0.045)], [0.052 (0.045)], [0.147], [0.025\*],
    [$gamma$], [0.099 (0.083)], [0.058 (0.065)], [0.058 (0.065)], [0.057 (0.060)], [0.185], [0.002\*],
    [$rho$],   [0.093 (0.125)], [0.051 (0.064)], [0.051 (0.064)], [0.045 (0.053)], [0.094], [0.326],

    table.cell(rowspan: 3)[0.001],
    [$beta$],  [0.079 (0.047)], [0.047 (0.048)], [0.047 (0.048)], [0.047 (0.047)], [0.075], [0.608],
    [$gamma$], [0.097 (0.094)], [0.064 (0.083)], [0.064 (0.083)], [0.065 (0.083)], [0.082], [0.492],
    [$rho$],   [0.062 (0.046)], [0.037 (0.043)], [0.037 (0.043)], [0.038 (0.044)], [0.055], [0.910],

    table.cell(rowspan: 9)[rf],
    table.cell(rowspan: 3)[0.1],
    [$beta$],  [0.068 (0.040)], [0.044 (0.040)], [0.045 (0.041)], [0.044 (0.039)], [0.102], [0.233],
    [$gamma$], [0.050 (0.074)], [0.029 (0.071)], [0.029 (0.072)], [0.029 (0.071)], [0.084], [0.463],
    [$rho$],   [0.158 (1.119)], [0.049 (0.291)], [0.047 (0.253)], [0.041 (0.207)], [0.109], [0.175],

    table.cell(rowspan: 3)[0.01],
    [$beta$],  [0.059 (0.026)], [0.034 (0.029)], [0.034 (0.029)], [0.034 (0.029)], [0.066], [0.760],
    [$gamma$], [0.035 (0.045)], [0.019 (0.032)], [0.019 (0.031)], [0.019 (0.032)], [0.067], [0.741],
    [$rho$],   [0.034 (0.030)], [0.019 (0.019)], [0.019 (0.018)], [0.019 (0.019)], [0.083], [0.469],

    table.cell(rowspan: 3)[0.001],
    [$beta$],  [0.059 (0.028)], [0.033 (0.031)], [0.033 (0.031)], [0.033 (0.031)], [0.076], [0.576],
    [$gamma$], [0.037 (0.061)], [0.023 (0.051)], [0.023 (0.051)], [0.023 (0.055)], [0.074], [0.621],
    [$rho$],   [0.027 (0.020)], [0.016 (0.018)], [0.016 (0.018)], [0.017 (0.018)], [0.064], [0.784],

    table.cell(rowspan: 9)[gb],
    table.cell(rowspan: 3)[0.1],
    [$beta$],  [0.070 (0.041)], [0.042 (0.040)], [0.047 (0.039)], [0.042 (0.039)], [0.064], [0.784],
    [$gamma$], [0.075 (0.115)], [0.046 (0.109)], [0.046 (0.108)], [0.046 (0.108)], [0.058], [0.864],
    [$rho$],   [0.501 (4.138)], [0.431 (3.847)], [0.426 (3.811)], [0.424 (3.773)], [0.078], [0.547],

    table.cell(rowspan: 3)[0.01],
    [$beta$],  [0.063 (0.029)], [0.036 (0.031)], [0.036 (0.031)], [0.036 (0.031)], [0.068], [0.722],
    [$gamma$], [0.056 (0.057)], [0.027 (0.033)], [0.027 (0.033)], [0.028 (0.034)], [0.055], [0.907],
    [$rho$],   [0.062 (0.065)], [0.032 (0.035)], [0.032 (0.035)], [0.031 (0.033)], [0.061], [0.832],

    table.cell(rowspan: 3)[0.001],
    [$beta$],  [0.062 (0.031)], [0.036 (0.033)], [0.036 (0.033)], [0.036 (0.033)], [0.087], [0.419],
    [$gamma$], [0.059 (0.075)], [0.034 (0.056)], [0.034 (0.056)], [0.033 (0.051)], [0.097], [0.281],
    [$rho$],   [0.046 (0.025)], [0.025 (0.021)], [0.025 (0.021)], [0.026 (0.022)], [0.106], [0.201],
  )
  #block(width:90%)[
    #set text(size: 8pt, font: fonts.sans_serif)
    #align(left)[
      RARMISE and RAE are given as the mean across 100 independent estimations
      with true values drawn from the prior (standard deviation in parentheses).
      \*$P < 0.05$ without correction for multiple testing; cf. (see histograms). \
      #super[a] Relative absolute root mean integrated squared error (see text)
      with respect to the true value. \
      #super[b] Relative absolute error with respect to the true value. \
      #super[c] Kolmogorov–Smirnov distance between empirical distribution of
      posterior probabilities of the true parameter and U(0, 1).
    ]
  ]
] <summary_stats_simulation_results_global>

=== Results
We have compared the performance of ABC with summary statistics chosen via PLS,
random forest (`rf`) and gradient boosting (`gb`) to that of ABC using
all candidate summary statistics @summary_stats_simulation_results_global. The RAE
behaved similarly for the three point estimates (mean, mode, and median) in good
and bad regimes. For assessment, we sought
low RARMISE and low RAE values, and require that the distribution of posterior
probabilities of the true value does not deviate from uniform for any parameter.
Across the compared methods, clear differences in both estimation accuracy and
posterior calibration are observed. The `all` and `pls` approaches
exhibit poor posterior calibration across $epsilon in {0.1, 0.01}$, as reflected in low KS
p-values and deviations from uniform coverage, indicating systematic bias and/or
over- or under-confidence in the resulting posterior distributions. In contrast,
both `rf` and `gb` yield substantially improved performance, but `rf`
achieves lower RAE and RARMISE values across parameters, indicating more accurate
and stable point and distributional estimates. Furthermore, `rf` shows
consistently high KS p-values, suggesting well-calibrated posteriors that are
consistent with the true parameter distributions. Overall, these results indicate
that `rf` provides the most reliable trade-off between accuracy and calibration,
and is therefore selected as the preferred method for subsequent analyses at the
$epsilon = 0.01$ regime.

=== Limitations
While the random forest and gradient boosting methods
performed well in this simulation study, their performance may depend on the
specific choice of hyperparameters (e.g., number of trees, depth of trees,
learning rate) and the size of the training dataset used for fitting the models.
More rigorous hyperparameter tuning could be conducted to potentially further
improve performance, though this would come at the cost of increased compute.
The regime with $epsilon = 0.001$ results in $100$ accepted simulations, which
may be insufficient for accurate density estimation, especially with a calibration
test of size 100. However, the results for this regime are broadly consistent with those
for $epsilon = 0.01$, which has a much larger number of accepted simulations,
and the overall conclusions regarding the relative performance of the methods are unchanged.

In addition, it has been shown by #cite(<2012Genet.192.1027A>) that locality
refinements can improve point estimate accuracy in regression-based ABC settings.
Aeschbacher et al. (2012) proposed an ABC framework with regression-based summary
statistics and locality refinement, where the training samples are taken from an
$epsilon$-neighbourhood around the observed summary statistics. This can improve the fidelity of
posterior mean estimates in many settings. Nevertheless, even without this additional
step, the resulting posterior approximations were well calibrated, with accurate
parameter recovery across simulation scenarios.

== Application to Data
Posteriors inferred for the provided observations dataset with the
explored methods and $epsilon = 0.01$ are shown in (@summary:marginal_kdes).
The marginal posteriors are well within the prior support and are very
concentrated. Point estimates and 95% highest posterior density (HPD) intervals
obtained with `rf` and `gb` are reported in @rf_posterior_estimates.
#figure(
  caption: [Posterior estimates for the provided data from ABC with summary
  statistics chosen globally via random forests (`rf`) and gradient boosting (`gb`)
  with acceptance rate $epsilon = 0.01$.]
)[
  #table(
    columns: 6,
    inset: (y: 4pt, x: 6pt),
    align: (left, left, left, left, left, center),
    [Method], [Parameter], [Mode], [Mean], [Median], [95% HPD interval],

    table.cell(rowspan: 3)[`rf`],
    [$beta$],  [0.1416], [0.1411], [0.1413], [(0.1287, 0.1563)],
    [$gamma$], [0.0876], [0.0876], [0.0876], [(0.0856, 0.0896)],
    [$rho$],   [0.2402], [0.2404], [0.2404], [(0.2277, 0.2520)],

    table.cell(rowspan: 3)[`gb`],
    [$beta$],  [0.1460], [0.1448], [0.1452], [(0.1287, 0.1606)],
    [$gamma$], [0.0857], [0.0863], [0.0863], [(0.0829, 0.0897)],
    [$rho$],   [0.2478], [0.2487], [0.2482], [(0.2297, 0.2691)],
  )
] <rf_posterior_estimates>

The marginal posterior obtained by `rf` is more concentrated than that obtained by `gb`
and there are some differences in the point estimates and HPD intervals. Compared to 'gb',
`rf` thinks that $beta$ is slightly lower, $gamma$ is slightly higher, and $rho$ is
slightly lower. 

=== Feature Importance
To investigate which summary statistics were most influential in the random
forest-based inference, we compare the feature importance scores from the fitted
random forest models given in @feature_importance. The most influential
statistic for $beta$ was `mean:initial_growth_rate` with a very high score of
0.990, capturing the infection rate signal without being confounded by the rewiring
dynamics. For $gamma$, the most influential statistic was `mean:auc_infected_fraction`
(0.782) followed by `sd:auc_infected_fraction` (0.119), and for $rho$, `mean:sd_degree` (0.735)
followed by `mean:peak_rewire_count` (0.159). Other summaries are not necessarily
uninformative or insufficient but feature importance scores are relative and depend on the fitted ensemble.
Therefore, it should be interpreted as a model-dependent measure rather than a
structural statement about sufficiency.

#figure(
  caption: [Marginal and joint pairwise posterior distributions inferred from the provided data.
  Posteriors obtained with tolerance $epsilon = 0.01$ and various methods for
  choosing summary statistics are compared. The dot-dashed red line corresponds
  to the method that performed best in the simulation study (`rf`;
  @summary_stats_simulation_results_global). Point
  estimates and 95% HPD intervals are given in @rf_posterior_estimates],
)[
  #image(
    "figures/summary/marginal_kdes.png",
    alt: "Margina posterior distributions for the provided data, comparing different methods for choosing summary statistics. The dot-dashed red line corresponds to the method that performed best in the simulation study (`rf`)."
  )
  #image(
    "figures/summary/rf_pairwise_joint.png",
    alt: "Pairwise joint posterior distributions for the provided data, obtained with tolerance $epsilon = 0.01$ and summary statistics chosen with learned random forests (rf)."
  )
] <summary:marginal_kdes>


#figure(
  caption: [Feature importance scores from the fitted random forest models used for summary statistic construction. The most influential statistics for each parameter are highlighted.],
)[
  #let a = rgb("#cf2406")
  #let cols = 4

  #let is-floatable(x) = (
    type(x) in (bool, decimal, float, int)
    or (type(x) == str and x.match(regex("\A-?(?:\d+|\d*\.\d*)\z")) != none)
  )

  #let tbl-content = (
    [Summary statistic], [$beta$], [$gamma$], [$rho$],

    [`mean:auc_infected_fraction`],         [0.000971], [0.782088], [0.000713],
    [`sd:auc_infected_fraction`],           [0.000784], [0.119448], [0.000257],
    [`mean:peak_infected_fraction`],        [0.000415], [0.008917], [0.000790],
    [`sd:peak_infected_fraction`],          [0.000449], [0.009251], [0.000251],
    [`mean:time_to_peak_infected_fraction`],[0.000380], [0.000675], [0.010183],
    [`sd:time_to_peak_infected_fraction`],  [0.000304], [0.000443], [0.000380],
    [`mean:initial_growth_ratio`],          [0.990066], [0.001505], [0.025429],
    [`sd:initial_growth_ratio`],            [0.000656], [0.003094], [0.000350],
    [`mean:peak_rewire_count`],             [0.000295], [0.000369], [0.159044],
    [`sd:peak_rewire_count`],               [0.000289], [0.000530], [0.009788],
    [`mean:time_to_peak_rewire_count`],     [0.000192], [0.039617], [0.024164],
    [`sd:time_to_peak_rewire_count`],       [0.000334], [0.000528], [0.000433],
    [`mean:total_rewire_count`],            [0.000148], [0.006622], [0.001383],
    [`sd:total_rewire_count`],              [0.000185], [0.006886], [0.000797],
    [`mean:mean_degree`],                   [0.000718], [0.000432], [0.000147],
    [`sd:mean_degree`],                     [0.000586], [0.000442], [0.000135],
    [`mean:sd_degree`],                     [0.000255], [0.000791], [0.735150],
    [`sd:sd_degree`],                       [0.000447], [0.003894], [0.000846],
    [`mean:rewire_to_infection_ratio`],     [0.000200], [0.009692], [0.002091],
    [`sd:rewire_to_infection_ratio`],       [0.000196], [0.000928], [0.000506],
    [`mean:lag_peak`],                      [0.001677], [0.003284], [0.026858],
    [`sd:lag_peak`],                        [0.000453], [0.000564], [0.000304],
  ).map(
    content => {
      let text = repr(content).slice(1, -1)
      if is-floatable(text) {
          let v = float(content.text)
          let ratio = 100% * (1 - calc.pow(v, 0.33))
          table.cell(
            fill: a.lighten(ratio)
          )[#text]
      } else {
        content
      }
      
    }
  )

  #table(
    columns: cols,
    align: (left, center, center, center),
    inset: (y: 4pt, x: 6pt),
    ..tbl-content
  )
] <feature_importance>
#pagebreak()