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

# Getting Started
To recreate the results in this project, follow these steps:
1. Clone the repository:
```bash
git clone www.github.com/chinzhening/sbi-adaptive-network-epidemic-model.git
```
2. Install the required dependencies. We recommend using a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
pip install -r requirements.txt
```
3. Build the source code:
```bash
./build.sh
```
4. Run the ABC experiments:
```bash
./run.sh experiments/[experiment_name].toml
```
5. The results and diagnostics will be saved in the output directory specified in the configuration file.
6. Run the modules in `analysis/scripts` to generate the figures and tables for the report.
```bash
python -m analysis.scripts.[script_name].py
``` 

# References
- [The ABC's of ABC (Approximate Bayesian Computation)](https://www.youtube.com/watch?v=MsgdXDXXP_0)