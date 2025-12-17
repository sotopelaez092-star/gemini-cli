#!/usr/bin/env python3
"""
Batch benchmark runner - runs multiple iterations and calculates statistics.

Usage:
    python batch_benchmark.py --cli aider --model deepseek/deepseek-chat --runs 3
    python batch_benchmark.py --cli claude --runs 3
    python batch_benchmark.py --cli pyfix --runs 3
"""

import argparse
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import statistics


def run_single_benchmark(cli: str, model: str, test_cases_dir: str, timeout: int, run_id: int) -> dict:
    """Run a single benchmark iteration."""
    cmd = [
        sys.executable,
        "scripts/run_benchmark.py",
        "--cli", cli,
        "--test-cases-dir", test_cases_dir,
        "--timeout", str(timeout),
    ]

    if model and cli in ("aider", "claude"):
        cmd.extend(["--model", model])

    print(f"\n{'='*60}")
    print(f"  RUN {run_id} - {cli} {model or ''}")
    print(f"{'='*60}")

    result = subprocess.run(
        cmd,
        capture_output=False,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Find the latest results file
    results_dir = Path(__file__).parent.parent / "results"
    json_files = sorted(results_dir.glob("summary_*.json"), key=os.path.getmtime, reverse=True)

    if json_files:
        with open(json_files[0]) as f:
            return json.load(f)

    return None


def main():
    parser = argparse.ArgumentParser(description="Run multiple benchmark iterations")
    parser.add_argument("--cli", choices=["gemini", "aider", "claude", "pyfix"], required=True)
    parser.add_argument("--model", default=None, help="Model to use (for aider/claude)")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs")
    parser.add_argument("--test-cases-dir", default="test_cases_v2")
    parser.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    results = []
    success_rates = []
    quality_scores = []
    durations = []

    for i in range(1, args.runs + 1):
        result = run_single_benchmark(
            cli=args.cli,
            model=args.model,
            test_cases_dir=args.test_cases_dir,
            timeout=args.timeout,
            run_id=i,
        )

        if result:
            results.append(result)
            success_rates.append(result.get("success_rate", 0))
            quality_scores.append(result.get("avg_quality_all", 0))
            durations.append(result.get("avg_duration_ms", 0))

    # Calculate statistics
    print("\n")
    print("=" * 60)
    print("  BATCH BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"CLI: {args.cli}")
    print(f"Model: {args.model or 'default'}")
    print(f"Runs: {args.runs}")
    print()

    if success_rates:
        print("SUCCESS RATE:")
        print(f"  Mean:   {statistics.mean(success_rates):.1f}%")
        print(f"  Median: {statistics.median(success_rates):.1f}%")
        if len(success_rates) > 1:
            print(f"  Std:    {statistics.stdev(success_rates):.1f}%")
        print(f"  Min:    {min(success_rates):.1f}%")
        print(f"  Max:    {max(success_rates):.1f}%")
        print(f"  All:    {[f'{r:.1f}%' for r in success_rates]}")
        print()

    if quality_scores:
        print("QUALITY SCORE:")
        print(f"  Mean:   {statistics.mean(quality_scores):.3f}")
        if len(quality_scores) > 1:
            print(f"  Std:    {statistics.stdev(quality_scores):.3f}")
        print()

    if durations:
        print("AVG DURATION:")
        print(f"  Mean:   {statistics.mean(durations)/1000:.1f}s")
        print()

    # Save batch results
    batch_result = {
        "cli": args.cli,
        "model": args.model,
        "runs": args.runs,
        "timestamp": datetime.now().isoformat(),
        "success_rate": {
            "mean": statistics.mean(success_rates) if success_rates else 0,
            "median": statistics.median(success_rates) if success_rates else 0,
            "std": statistics.stdev(success_rates) if len(success_rates) > 1 else 0,
            "min": min(success_rates) if success_rates else 0,
            "max": max(success_rates) if success_rates else 0,
            "all": success_rates,
        },
        "quality": {
            "mean": statistics.mean(quality_scores) if quality_scores else 0,
            "std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
        },
        "duration_ms": {
            "mean": statistics.mean(durations) if durations else 0,
        },
        "individual_results": results,
    }

    # Save to file
    results_dir = Path(__file__).parent.parent / "results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_file = results_dir / f"batch_{args.cli}_{timestamp}.json"

    with open(batch_file, "w") as f:
        json.dump(batch_result, f, indent=2)

    print(f"Batch results saved to: {batch_file}")


if __name__ == "__main__":
    main()
