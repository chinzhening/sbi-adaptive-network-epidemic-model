# Simulation Based Inference For An Adpative Network Epidemic Model
This repository contains the code for the [final project](https://alexxthiery.github.io/teaching/SBI_infection/SBI-infection.html) of the course "ST3247 Simulation",
read under Prof. Alex Thiery in AY2025/2026 Semester 2.

# Overview
Statistical inference in situations where the likelihood function is intractable is a common problem in many scientific domains.
Simulation-based inference (SBI) methods, such as [Approximate Bayesian Computation](https://en.wikipedia.org/wiki/Approximate_Bayesian_computation) (ABC), have been developed to address this issue.
In this project, we apply SBI methods to an adaptive network epidemic model, which captures the dynamics of disease spread while allowing for changes in the contact network structure.

In general, there is no guarantee that SBI methods are able to recover the true parameters of the model.
We investigate the performance of the basic ABC rejection algorithm, choosing of the summary statistics, distance function, and tolerance. We compare the results with more sophisticated methods such as:

TODO: add more details about the advanced methods, e.g. ABC-SMC, ABC-MCMC, regression adjustment.

# Repository Structure
The repository is organized as follows:
```
├── data/                   # datasets used in the project
├── report/                 # source files for the final report
├── src/                    # source code for simulations and inference methods
│   ├── abctools/           # implementation of ABC algorithms
├── experiments/            # scripts to run experiments and generate results
|   eda.ipynb               # exploratory data analysis notebook
```

# Getting Started
To recreate the results in this project, clone the repo and follow these steps:
1. Setup the project with `uv`:
   ```
   uv sync
   ```
2. Run the experiments as a python module:
   ```
   python -m experiments.rejection_01
   ```
3. Check the results in the `results/` directory.

# References
- [The ABC's of ABC (Approximate Bayesian Computation)](https://www.youtube.com/watch?v=MsgdXDXXP_0)