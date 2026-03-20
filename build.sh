#!/usr/bin/env bash
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Configuring..."
cmake -S "$SCRIPT_DIR" -B "$SCRIPT_DIR/build" -DCMAKE_BUILD_TYPE=Release

echo "Building..."
cmake --build "$SCRIPT_DIR/build" --parallel

echo "Done. Executable is at $SCRIPT_DIR/build/simulate"