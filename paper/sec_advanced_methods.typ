#import "template.typ":*

#part("Advanced Methods")
You are tasked with exploring more advanced simulation-based inference methods. The goal is to improve the quality of your parameter estimates beyond what basic rejection ABC achieves. For example, some possible approaches (but these are by no means the only ones) include:

#set cite(form: "year")
#list(
  [*Regression adjustment.* Post-processing ABC samples using local linear regression to correct for the gap between simulated and observed summaries. This can sharpen posteriors without additional simulations. See Beaumont, Zhang, and Balding (#cite(<Beaumont2002-ax>)).],
  [*ABC-MCMC.* Instead of independent rejection sampling, use a Markov chain Monte Carlo sampler within the ABC framework. This can be more efficient than rejection ABC because proposed parameters are informed by the current state of the chain, rather than drawn blindly from the prior. The original algorithm is due to Marjoram et al. (#cite(<Marjoram2003-ga>)).],
  [*SMC-ABC (Sequential Monte Carlo ABC).* Run ABC with a sequence of decreasing tolerance thresholds, using a population of particles that are resampled and perturbed at each step. This is often more efficient than rejection ABC for reaching small tolerances. See, e.g., Sisson, Fan, and Tanaka (#cite(<Sisson2007-aa>)) or Beaumont et al. (#cite(<Beaumont2009-mi>)).],
  [*Synthetic likelihood.* Instead of comparing summary statistics through a distance function, assume that the summary statistics follow a multivariate normal distribution (conditional on the parameters) and estimate the mean and covariance from repeated simulations. This defines an approximate likelihood that can be used in standard MCMC. See Wood (#cite(<Wood2010-me>)).],
)
You are encourage to explore widely, do sanity checks, and compare the results of different methods. The goal is to demonstrate that you understand the limitations of basic ABC and how more advanced methods can improve inference quality.

#pagebreak()