#import "template.typ":*

#part("Summary Statistics")
The choice of summary statistics is one of the most important design decision in ABC.
Poorly chosen summaries lose information about the parameters; good summaries compress the data while retaining discriminative power.

A key challenge in this model: 
$beta$ and $rho$ 
can both suppress the epidemic through different mechanisms.
Summary statistics based only on the infected fraction time series cannot fully separate these two parameters.
The rewiring counts and degree histograms carry additional information.

Investigate which summaries are informative for which parameters. Compare different sets of summaries and show how the choice affects the posterior.

#pagebreak()