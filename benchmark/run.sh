#!/bin/bash
# Gemini CLI Python Error Fixing Benchmark
# Usage: ./run.sh [--error-type name_error] [--parallel 2]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "Gemini CLI Cross-File Python Debug Benchmark"
echo "=============================================="
echo ""

# Check if gemini is available
if ! command -v gemini &> /dev/null; then
    echo "Error: 'gemini' command not found"
    echo "Please install Gemini CLI first: npm install -g @anthropic/gemini-cli"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

echo "Starting benchmark..."
echo ""

# Run benchmark
python3 scripts/run_benchmark.py \
    --test-cases-dir ./test_cases \
    --results-dir ./results \
    "$@"

echo ""
echo "Generating detailed analysis..."
python3 scripts/analyze_results.py --results-dir ./results

echo ""
echo "Benchmark complete!"
