#!/usr/bin/env python3
"""
Batch benchmark runner - runs multiple iterations and calculates statistics.

Features:
- Real-time progress display
- Parallel test execution
- Resume from interruption
- Detailed statistics

Usage:
    python benchmark/scripts/batch_benchmark.py --cli aider --model deepseek/deepseek-chat --runs 3
    python benchmark/scripts/batch_benchmark.py --cli pyfix --runs 3 --parallel
    python benchmark/scripts/batch_benchmark.py --cli claude --runs 3 --resume
"""

import argparse
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import statistics
import glob


def get_benchmark_dir():
    """Get the benchmark directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def run_single_benchmark(cli: str, model: str, test_cases_dir: str, timeout: int,
                         run_id: int, total_runs: int, parallel: int) -> dict:
    """Run a single benchmark iteration."""
    benchmark_dir = get_benchmark_dir()

    cmd = [
        sys.executable,
        str(benchmark_dir / "scripts" / "run_benchmark.py"),
        "--cli", cli,
        "--test-cases-dir", str(benchmark_dir / test_cases_dir),
        "--timeout", str(timeout),
    ]

    if model and cli in ("aider", "claude"):
        cmd.extend(["--model", model])

    if parallel > 1:
        cmd.extend(["--parallel", str(parallel)])

    print(f"\n{'='*60}")
    print(f"  RUN {run_id}/{total_runs} - {cli} {model or 'default'}")
    print(f"{'='*60}\n")

    result = subprocess.run(
        cmd,
        capture_output=False,
        text=True,
    )

    # Find the latest results file
    results_dir = benchmark_dir / "results"
    json_files = sorted(results_dir.glob("summary_*.json"), key=os.path.getmtime, reverse=True)

    if json_files:
        with open(json_files[0]) as f:
            data = json.load(f)
            data["_result_file"] = str(json_files[0])
            return data

    return None


def find_existing_runs(cli: str, model: str, results_dir: Path) -> list:
    """Find existing batch run results for resume."""
    pattern = f"batch_{cli}_*.json"
    existing_files = sorted(results_dir.glob(pattern), key=os.path.getmtime, reverse=True)

    for f in existing_files:
        with open(f) as fp:
            data = json.load(fp)
            if data.get("model") == model and not data.get("completed", True):
                return data.get("individual_results", []), f

    return [], None


def print_statistics(success_rates: list, quality_scores: list, durations: list,
                     cli: str, model: str, runs: int):
    """Print formatted statistics."""
    print("\n")
    print("=" * 60)
    print("  BATCH BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"  CLI:    {cli}")
    print(f"  Model:  {model or 'default'}")
    print(f"  Runs:   {len(success_rates)}/{runs}")
    print("=" * 60)

    if success_rates:
        print("\n📊 SUCCESS RATE:")
        print(f"  ├─ Mean:   {statistics.mean(success_rates):.1f}%")
        print(f"  ├─ Median: {statistics.median(success_rates):.1f}%")
        if len(success_rates) > 1:
            print(f"  ├─ Std:    {statistics.stdev(success_rates):.1f}%")
        print(f"  ├─ Min:    {min(success_rates):.1f}%")
        print(f"  ├─ Max:    {max(success_rates):.1f}%")
        print(f"  └─ All:    {[f'{r:.1f}%' for r in success_rates]}")

    if quality_scores:
        print("\n⭐ QUALITY SCORE:")
        print(f"  ├─ Mean:   {statistics.mean(quality_scores):.3f}")
        if len(quality_scores) > 1:
            print(f"  └─ Std:    {statistics.stdev(quality_scores):.3f}")
        else:
            print(f"  └─ (need more runs for std)")

    if durations:
        print("\n⏱️  AVG DURATION:")
        print(f"  └─ Mean:   {statistics.mean(durations)/1000:.1f}s")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run multiple benchmark iterations")
    parser.add_argument("--cli", choices=["gemini", "aider", "claude", "pyfix"], required=True,
                        help="CLI tool to test")
    parser.add_argument("--model", default=None,
                        help="Model to use (for aider/claude)")
    parser.add_argument("--runs", type=int, default=3,
                        help="Number of runs (default: 3)")
    parser.add_argument("--test-cases-dir", default="test_cases_v2",
                        help="Test cases directory (default: test_cases_v2)")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Timeout per test case in seconds (default: 300)")
    parser.add_argument("--parallel", type=int, default=1,
                        help="Number of parallel test runs within each batch (default: 1)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from previous incomplete run")

    args = parser.parse_args()

    benchmark_dir = get_benchmark_dir()
    results_dir = benchmark_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # Check for resume
    results = []
    resume_file = None
    start_run = 1

    if args.resume:
        results, resume_file = find_existing_runs(args.cli, args.model, results_dir)
        if results:
            start_run = len(results) + 1
            print(f"📂 Resuming from run {start_run} (found {len(results)} completed runs)")

    success_rates = [r.get("success_rate", 0) for r in results]
    quality_scores = [r.get("avg_quality_all", 0) for r in results]
    durations = [r.get("avg_duration_ms", 0) for r in results]

    # Run benchmarks
    try:
        for i in range(start_run, args.runs + 1):
            result = run_single_benchmark(
                cli=args.cli,
                model=args.model,
                test_cases_dir=args.test_cases_dir,
                timeout=args.timeout,
                run_id=i,
                total_runs=args.runs,
                parallel=args.parallel,
            )

            if result:
                results.append(result)
                success_rates.append(result.get("success_rate", 0))
                quality_scores.append(result.get("avg_quality_all", 0))
                durations.append(result.get("avg_duration_ms", 0))

                # Print interim statistics
                print_statistics(success_rates, quality_scores, durations,
                               args.cli, args.model, args.runs)

            # Save progress after each run (for resume)
            batch_result = {
                "cli": args.cli,
                "model": args.model,
                "runs": args.runs,
                "completed": i == args.runs,
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_suffix = f"_{args.model.replace('/', '_')}" if args.model else ""
            batch_file = results_dir / f"batch_{args.cli}{model_suffix}_{timestamp}.json"

            with open(batch_file, "w") as f:
                json.dump(batch_result, f, indent=2)

            print(f"\n💾 Progress saved to: {batch_file.name}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted! Progress has been saved.")
        print(f"   Use --resume to continue from run {len(results) + 1}")
        print_statistics(success_rates, quality_scores, durations,
                        args.cli, args.model, args.runs)

    # Final summary
    if len(success_rates) == args.runs:
        print("\n✅ All runs completed!")

    print(f"\n📁 Results saved to: {results_dir}")


if __name__ == "__main__":
    main()
