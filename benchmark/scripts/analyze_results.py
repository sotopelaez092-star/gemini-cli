#!/usr/bin/env python3
"""
Analyze benchmark results and generate reports.

Usage:
    python analyze_results.py --results-dir ./results [--compare]
"""

import argparse
import json
from pathlib import Path
from typing import Optional


def load_latest_results(results_dir: Path) -> tuple[list, dict]:
    """Load the most recent results and summary files."""
    results_files = sorted(results_dir.glob("results_*.json"), reverse=True)
    summary_files = sorted(results_dir.glob("summary_*.json"), reverse=True)

    if not results_files or not summary_files:
        raise FileNotFoundError("No results found in the directory")

    with open(results_files[0]) as f:
        results = json.load(f)

    with open(summary_files[0]) as f:
        summary = json.load(f)

    return results, summary


def print_detailed_report(results: list, summary: dict):
    """Print detailed analysis report."""
    print("\n" + "=" * 70)
    print("DETAILED BENCHMARK ANALYSIS")
    print("=" * 70)

    # Overall stats
    print(f"\nTimestamp: {summary['timestamp']}")
    print(f"Total Cases: {summary['total_cases']}")
    print(f"Overall Success Rate: {summary['success_rate']:.1f}%")

    # Performance metrics
    print("\n--- Performance Metrics ---")
    print(f"Average Duration: {summary['avg_duration_ms']:.0f}ms ({summary['avg_duration_ms']/1000:.1f}s)")
    print(f"Average Tokens: {summary['avg_tokens']:.0f}")

    # By error type table
    print("\n--- Results by Error Type ---")
    print(f"{'Error Type':<20} {'Success':<10} {'Rate':<10} {'Avg Time':<12} {'Avg Tokens':<12}")
    print("-" * 70)

    for error_type, stats in summary["by_error_type"].items():
        rate = f"{stats['success_rate']:.0f}%"
        success = f"{stats['passed']}/{stats['total']}"
        time_str = f"{stats['avg_duration_ms']:.0f}ms"
        tokens = f"{stats['avg_tokens']:.0f}"
        print(f"{error_type:<20} {success:<10} {rate:<10} {time_str:<12} {tokens:<12}")

    # Failed cases
    failed_results = [r for r in results if not r["success"]]
    if failed_results:
        print("\n--- Failed Cases ---")
        for r in failed_results:
            print(f"\n  Case: {r['case_id']}")
            print(f"  Error Type: {r['error_type']}")
            print(f"  Fix Applied: {r['fix_applied']}")
            print(f"  Verification: {r['verification_passed']}")
            if r["error_message"]:
                print(f"  Error: {r['error_message'][:100]}...")

    # Slow cases
    print("\n--- Slowest Cases ---")
    sorted_by_time = sorted(results, key=lambda x: x["duration_ms"], reverse=True)[:5]
    for r in sorted_by_time:
        print(f"  {r['case_id']}: {r['duration_ms']:.0f}ms ({r['duration_ms']/1000:.1f}s)")

    # Token usage
    print("\n--- Highest Token Usage ---")
    sorted_by_tokens = sorted(results, key=lambda x: x["tokens_used"], reverse=True)[:5]
    for r in sorted_by_tokens:
        print(f"  {r['case_id']}: {r['tokens_used']} tokens")

    print("\n" + "=" * 70)


def compare_runs(results_dir: Path):
    """Compare multiple benchmark runs."""
    summary_files = sorted(results_dir.glob("summary_*.json"))

    if len(summary_files) < 2:
        print("Need at least 2 runs to compare")
        return

    print("\n--- Run Comparison ---")
    print(f"{'Timestamp':<25} {'Success Rate':<15} {'Avg Duration':<15} {'Avg Tokens':<15}")
    print("-" * 70)

    for f in summary_files[-5:]:  # Last 5 runs
        with open(f) as fp:
            s = json.load(fp)
        print(f"{s['timestamp']:<25} {s['success_rate']:.1f}%{'':<9} {s['avg_duration_ms']:.0f}ms{'':<10} {s['avg_tokens']:.0f}")


def generate_markdown_report(results: list, summary: dict, output_file: Path):
    """Generate a markdown report."""
    with open(output_file, "w") as f:
        f.write("# Gemini CLI Python Error Fixing Benchmark Report\n\n")
        f.write(f"**Date:** {summary['timestamp']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total Cases | {summary['total_cases']} |\n")
        f.write(f"| Passed | {summary['passed']} |\n")
        f.write(f"| Failed | {summary['failed']} |\n")
        f.write(f"| Success Rate | {summary['success_rate']:.1f}% |\n")
        f.write(f"| Avg Duration | {summary['avg_duration_ms']:.0f}ms |\n")
        f.write(f"| Avg Tokens | {summary['avg_tokens']:.0f} |\n\n")

        f.write("## Results by Error Type\n\n")
        f.write("| Error Type | Success Rate | Avg Duration | Avg Tokens |\n")
        f.write("|------------|--------------|--------------|------------|\n")
        for error_type, stats in summary["by_error_type"].items():
            f.write(f"| {error_type} | {stats['success_rate']:.0f}% ({stats['passed']}/{stats['total']}) | {stats['avg_duration_ms']:.0f}ms | {stats['avg_tokens']:.0f} |\n")

        f.write("\n## Detailed Results\n\n")
        f.write("| Case ID | Error Type | Success | Duration | Tokens |\n")
        f.write("|---------|------------|---------|----------|--------|\n")
        for r in results:
            status = "✅" if r["success"] else "❌"
            f.write(f"| {r['case_id']} | {r['error_type']} | {status} | {r['duration_ms']:.0f}ms | {r['tokens_used']} |\n")

    print(f"\nMarkdown report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze benchmark results")
    parser.add_argument(
        "--results-dir",
        default="./results",
        help="Directory containing results",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple runs",
    )
    parser.add_argument(
        "--markdown",
        type=str,
        help="Generate markdown report to specified file",
    )

    args = parser.parse_args()
    results_dir = Path(args.results_dir)

    if args.compare:
        compare_runs(results_dir)
    else:
        results, summary = load_latest_results(results_dir)
        print_detailed_report(results, summary)

        if args.markdown:
            generate_markdown_report(results, summary, Path(args.markdown))


if __name__ == "__main__":
    main()
