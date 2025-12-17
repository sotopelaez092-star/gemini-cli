#!/usr/bin/env python3
"""
Simple Claude Code benchmark script.

Usage:
    python benchmark/scripts/test_claude.py
    python benchmark/scripts/test_claude.py --error-type name_error
    python benchmark/scripts/test_claude.py --runs 3
"""

import subprocess
import json
import os
import sys
import shutil
import time
from pathlib import Path
from datetime import datetime


def run_python_and_check(work_dir: Path, main_file: str = "main.py") -> tuple[bool, str]:
    """Run python and return (success, error_message)."""
    try:
        result = subprocess.run(
            [sys.executable, main_file],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "PYTHONPATH": str(work_dir)},
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)


def run_claude(work_dir: Path, prompt: str, timeout: int = 300) -> tuple[bool, str, float]:
    """Run Claude Code and return (success, output, duration)."""
    cmd = [
        "claude",
        "--print",
        "--dangerously-skip-permissions",
        prompt,
    ]

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
        duration = time.time() - start

        if result.returncode == 0:
            return True, result.stdout, duration
        return False, result.stderr or result.stdout, duration

    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s", time.time() - start
    except Exception as e:
        return False, str(e), time.time() - start


def run_single_test(case_dir: Path, timeout: int = 300) -> dict:
    """Run a single test case."""
    case_id = case_dir.name

    # Load metadata
    metadata_file = case_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
        error_file = metadata.get("error_file", "main.py")
    else:
        error_file = "main.py"

    # Create workspace copy
    workspace_dir = Path("/tmp/claude_test") / case_id
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
    shutil.copytree(case_dir, workspace_dir)

    # Get original error
    _, original_error = run_python_and_check(workspace_dir, error_file)

    # Build prompt
    prompt = f"""Fix the Python error in {error_file}.
The error when running 'python {error_file}' is:
{original_error[:1000]}

Please fix the bug and save the changes."""

    # Run Claude
    print(f"  Running Claude on {case_id}...", end=" ", flush=True)
    success, output, duration = run_claude(workspace_dir, prompt, timeout)

    if not success:
        print(f"❌ Claude failed ({duration:.1f}s)")
        return {
            "case_id": case_id,
            "passed": False,
            "duration": duration,
            "error": output[:500],
        }

    # Verify fix
    fixed, verify_error = run_python_and_check(workspace_dir, error_file)

    if fixed:
        print(f"✅ Passed ({duration:.1f}s)")
        return {
            "case_id": case_id,
            "passed": True,
            "duration": duration,
        }
    else:
        print(f"❌ Not fixed ({duration:.1f}s)")
        return {
            "case_id": case_id,
            "passed": False,
            "duration": duration,
            "error": verify_error[:500],
        }


def discover_cases(test_cases_dir: Path, error_type: str = None) -> list[Path]:
    """Discover test cases."""
    cases = []
    for error_dir in sorted(test_cases_dir.iterdir()):
        if not error_dir.is_dir():
            continue
        if error_type and error_type.lower() not in error_dir.name.lower():
            continue
        for case_dir in sorted(error_dir.iterdir()):
            if case_dir.is_dir() and (case_dir / "main.py").exists():
                cases.append(case_dir)
    return cases


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-cases-dir", default="benchmark/test_cases_v2")
    parser.add_argument("--error-type", default=None, help="Filter by error type (e.g., name_error)")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--runs", type=int, default=1, help="Number of runs for batch testing")
    args = parser.parse_args()

    # Find test cases dir
    script_dir = Path(__file__).parent
    if Path(args.test_cases_dir).is_absolute():
        test_cases_dir = Path(args.test_cases_dir)
    else:
        test_cases_dir = script_dir.parent.parent / args.test_cases_dir
        if not test_cases_dir.exists():
            test_cases_dir = Path(args.test_cases_dir)

    print(f"Test cases dir: {test_cases_dir}")

    # Discover cases
    cases = discover_cases(test_cases_dir, args.error_type)
    print(f"Found {len(cases)} test cases\n")

    all_results = []

    for run_num in range(1, args.runs + 1):
        if args.runs > 1:
            print(f"\n{'='*60}")
            print(f"  RUN {run_num}/{args.runs}")
            print(f"{'='*60}")

        results = []
        for case in cases:
            result = run_single_test(case, args.timeout)
            results.append(result)

        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        avg_duration = sum(r["duration"] for r in results) / total if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"  RESULTS: {passed}/{total} ({success_rate:.1f}%)")
        print(f"  Avg Duration: {avg_duration:.1f}s")
        print(f"{'='*60}")

        # Show failures
        failures = [r for r in results if not r["passed"]]
        if failures:
            print(f"\nFailed cases ({len(failures)}):")
            for f in failures:
                print(f"  - {f['case_id']}: {f.get('error', 'Unknown')[:100]}")

        all_results.append({
            "run": run_num,
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "results": results,
        })

    # Summary for multiple runs
    if args.runs > 1:
        rates = [r["success_rate"] for r in all_results]
        import statistics
        print(f"\n{'='*60}")
        print(f"  BATCH SUMMARY ({args.runs} runs)")
        print(f"{'='*60}")
        print(f"  Mean:   {statistics.mean(rates):.1f}%")
        print(f"  Min:    {min(rates):.1f}%")
        print(f"  Max:    {max(rates):.1f}%")
        if len(rates) > 1:
            print(f"  Std:    {statistics.stdev(rates):.1f}%")
        print(f"  All:    {[f'{r:.1f}%' for r in rates]}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = test_cases_dir.parent / "results" / f"claude_test_{timestamp}.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
