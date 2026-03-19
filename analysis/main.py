import argparse

from pathlib import Path
from config import load_plot_config, reconstruct_result
from plots import generate_diagnostics

def main():
    """
    Main entry point for the analysis script.
    Parses command-line arguments, loads the configuration and results, generates
    diagnostics and posterior statistics, and saves the generated plots.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--config",  required=True)
    parser.add_argument("--output",  required=True)
    args = parser.parse_args()

    output_dir = Path(args.output)

    cfg    = load_plot_config(args.config)
    result = reconstruct_result(args.results, cfg)

    diagnostics, posterior_stats = generate_diagnostics(result)

    diagnostics["distance_histogram"].savefig(output_dir / "distance_histogram.png")
    diagnostics["accepted_params_pairwise_plot"].savefig(output_dir / "pairwise.png")
    diagnostics["params_kde_and_ci"].savefig(output_dir / "kde_ci.png")

    print(posterior_stats)

if __name__ == "__main__":
    main()