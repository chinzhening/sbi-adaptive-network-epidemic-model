#import "template.typ":*

#show: appendix

#part("Appendix") <appendix:a>
The code used for all simulations and analyses in this report is available at my
github
#underline[#link("https://github.com/chinzhening/sbi-adaptive-network-epidemic-model")[repository]] along with
documentation for reproducing the results.
 \
#figure(
  caption: "Summary statistics, their descriptions, and intuition.",
)[
  #set text(size: 8pt)

  #table(
    columns: (1fr, 1fr, 2fr, 1.5fr),
    align: (left, right, left, left),
    inset: (y: 4pt, x: 6pt),

    [Name], [Formula], [Description], [Intuition],

    [Peak infected fraction], [$max_t I_t$],
    [Max infected fraction],
    [Outbreak severity (β, ρ)],

    [Time to peak infection], [$arg max I_t$],
    [Time of peak infection],
    [Epidemic speed indicator],

    [Area under infection curve], [$sum_t I_t$],
    [Integral of infected fraction over time],
    [Total epidemic burden],

    [Initial growth ratio], [$I_1 \/ I_0$],
    [],
    [Early transmission rate (β-driven)],

    [Total rewire count], [$sum_t R_t$],
    [Total rewiring events],
    [Overall behavioral adaptation (ρ)],

    [Peak rewire count], [$max_t R_t$],
    [Max rewiring in a single step],
    [Peak avoidance intensity],

    [Time to peak rewire], [$arg max R_t$],
    [Time of peak rewiring],
    [Timing of behavioral response],

    [Rewire / infection ratio], [],
    [Total rewiring / total infections],
    [Adaptation vs transmission strength],

    [Peak lag], [$max_t I_t - max_t R_t$],
    [Time difference between peaks],
    [Response delay of behavior],

    [Mean final degree], [$mu_"deg"$],
    [Mean node degree at final time],
    [Residual connectivity],

    [SD final degree], [$sigma_"deg"$],
    [Std. dev. of final degree],
    [Network heterogeneity (ρ-driven)],
  )
]
<summary_stats_desc>