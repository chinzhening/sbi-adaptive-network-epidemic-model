#import "template.typ":*

#part("Rejection ABC")
Implement rejection ABC to obtain an approximate posterior over $(beta, gamma, rho)$.
The algorithm repeatedly draws parameters from the prior, simulates data, computes summary statistics, and accepts parameters whose simulated summaries are close enough to the observed ones, as described in class.
You will need to make choices about summary statistics, distance function, normalization, and tolerance.
Document these choices and present the resulting approximate posterior (marginal histograms, pairwise plots). 
Discuss the quality of the estimates.

#pagebreak()