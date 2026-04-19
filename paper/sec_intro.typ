#import "template.typ": *

#part("Introduction")

Accurate modeling of infectious disease spread remains a central problem in
epidemiology. Classical SIR frameworks assume homogeneous mixing or static
contact networks #cite(<anderson1991infectious>), yet individuals routinely
adapt their behaviour during an epidemic — avoiding infected contacts or
seeking new ones — in ways that directly alter transmission pathways
#cite(<gross2006epidemic>). The adaptive-network SIR model captures this
feedback by coupling epidemic dynamics with network evolution: susceptible
nodes may rewire connections away from infected neighbours, reflecting
behavioural avoidance. This co-evolution of states and structure creates a
nontrivial identifiability problem, as distinct combinations of infection,
recovery, and rewiring rates can produce similar observed dynamics.

// [FIGURE: example trajectories showing two parameter sets with similar
//  infected-fraction time series but different rewiring counts, illustrating
//  the identifiability problem]

We consider the problem of inferring model parameters from partially observed
epidemic realisations. The likelihood of the observed data is intractable,
requiring integration over all latent network configurations and epidemic
trajectories under path-dependent dynamics. We therefore employ Approximate
Bayesian Computation (ABC) #cite(<Beaumont2002-ax>), which replaces likelihood
evaluation with simulation-based comparison of summary statistics.

This report proceeds as follows. We begin with rejection ABC as a baseline
posterior approximation, then examine summary statistic construction under the
semi-automatic framework of #cite(<fearnhead2012semiabc>) and evaluate
performance across methods. Finally, we apply neural posterior estimation (NPE)
as a more sample-efficient alternative (cite).

== Model
We consider an adaptive-network SIR model on a contact network of $N = 200$
nodes, with edges representing potential transmission pathways. At each
discrete time step, three processes occur in parallel: susceptible nodes (S)
adjacent to infected nodes (I) become infected with probability $beta$; infected
nodes recover with probability $gamma$; and each S–I edge is rewired with
probability $rho$, redirecting the susceptible node toward a uniformly chosen
non-neighbour. Recovered individuals (R) remain in the recovered state. The
three parameters and their priors are summarised in @model_parameters_desc.

#figure(
  caption: "Model parameters and network evolution dynamics.",
)[
  #table(
    columns: (auto, auto, auto),
    align: (left, left, left),

    [Parameter], [Description], [Prior],

    [$beta$ (infection)], [Each susceptible neighbor of an infected agent becomes infected with probability $beta$. New infections are applied after all attempts are evaluated.], [Unif(0.05, 0.50)],
    [$gamma$ (recovery)], [Each infected individual (excluding those infected in the current time step) recovers with probability $gamma$.], [Unif(0.02, 0.20)],
    [$rho$ (rewiring)], [For each S-I edge, with probability $rho$, the connection is rewired to a uniformly random non-neighbour.], [Unif(0.0, 0.80)],
  )
] <model_parameters_desc>

== Simulation
The network is initialised as an Erdős–Rényi graph $G(200, 0.05)$ with
$n_0 = 5$ infected nodes and simulated for $T = 200$ time steps. Observational
data are generated from $R = 40$ independent replicates under the same unknown
parameter vector $(beta, gamma, rho)$. For each replicate, the following are
recorded: the time series of the infected fraction $I(t)\/N$, the rewiring
event count at each step, and the final degree distribution of the network.
Summary statistics for ABC are derived from these quantities; the goal is to
recover the true $(beta, gamma, rho)$ governing the epidemic.

To improve the computational efficiency of the adaptive network model simulator,
we reimplemented it in `C++` and ran the simulations in parallel on a local machine,
which allowed us to generate the large number of simulation ($N=10^5$) required
for ABC inference in a reasonable timeframe ($tilde$ 25 minutes). These simulations
were stored in a reference table for subsequent ABC analyses, which allowed us
to experiment with different summary statistic designs and distance metrics
without needing to rerun the simulations. The code for the C++ implementation
and parallel simulation is provided in @appendix:a. 