#!/usr/bin/env bash
set -euo pipefail

CONFIG=${1:-config.toml}
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Configuring..."
cmake -S "$SCRIPT_DIR" -B "$SCRIPT_DIR/build" -DCMAKE_BUILD_TYPE=Release

echo "Building..."
cmake --build "$SCRIPT_DIR/build" --parallel

echo "Running ABC sampler..."
"$SCRIPT_DIR/build/abc_sampler" "$CONFIG"

# read output dir from run_info.txt
OUTPUT_DIR=$(grep "output_dir=" results/*/*/run_info.txt | tail -1 | cut -d= -f2)

echo "Generating diagnostics..."
python3 "$SCRIPT_DIR/analysis/main.py" \
    --results "$OUTPUT_DIR/abc_results.csv" \
    --config  "$OUTPUT_DIR/config.toml" \
    --output  "$OUTPUT_DIR"

echo "Done. Results in $OUTPUT_DIR"