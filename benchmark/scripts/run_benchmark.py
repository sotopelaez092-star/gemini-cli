#!/usr/bin/env python3
"""
AI CLI Cross-File Python Debug Benchmark Runner

Supports: Gemini CLI, Aider

Usage:
    python run_benchmark.py [--error-type NAME_ERROR] [--parallel 4] [--timeout 120]
    python run_benchmark.py --cli aider --model openai/gemini-2.0-flash
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class TestResult:
    case_id: str
    error_type: str
    success: bool
    duration_ms: float
    tokens_used: int
    tool_calls: int
    error_message: Optional[str] = None
    fix_applied: bool = False
    verification_passed: bool = False
    gemini_response: str = ""
    raw_output: dict = field(default_factory=dict)


@dataclass
class BenchmarkSummary:
    total_cases: int
    passed: int
    failed: int
    success_rate: float
    avg_duration_ms: float
    avg_tokens: float
    by_error_type: dict = field(default_factory=dict)
    timestamp: str = ""


class BenchmarkRunner:
    """Run benchmarks against AI CLI tools for Python error fixing."""

    def __init__(
        self,
        test_cases_dir: str,
        results_dir: str,
        cli_tool: str = "gemini",  # "gemini" or "aider"
        gemini_cmd: str = "gemini",
        aider_model: str = "openai/gemini-2.0-flash",
        timeout: int = 120,
        parallel: int = 1,
    ):
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        self.cli_tool = cli_tool
        self.gemini_cmd = gemini_cmd
        self.aider_model = aider_model
        self.timeout = timeout
        self.parallel = parallel
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def discover_test_cases(self, error_type: Optional[str] = None) -> list[Path]:
        """Discover all test cases, optionally filtered by error type."""
        cases = []
        for error_dir in self.test_cases_dir.iterdir():
            if not error_dir.is_dir():
                continue
            if error_type and error_dir.name != error_type.lower():
                continue
            for case_dir in error_dir.iterdir():
                if case_dir.is_dir() and (case_dir / "metadata.json").exists():
                    cases.append(case_dir)
        return sorted(cases)

    def run_single_test(self, case_dir: Path) -> TestResult:
        """Run a single test case."""
        # Load metadata
        with open(case_dir / "metadata.json") as f:
            metadata = json.load(f)

        case_id = metadata["case_id"]
        error_type = metadata["error_type"]
        error_file = metadata.get("error_file", "main.py")

        print(f"  Running: {case_id} ({error_type})")

        # Create a temporary working copy
        work_dir = self.results_dir / "workspaces" / case_id
        if work_dir.exists():
            shutil.rmtree(work_dir)
        shutil.copytree(case_dir, work_dir)

        # Generate the error by running the code
        error_output = self._capture_python_error(work_dir, error_file)

        # Build the prompt for Gemini
        prompt = self._build_fix_prompt(work_dir, error_file, error_output, metadata)

        # Run AI CLI tool
        start_time = time.time()
        if self.cli_tool == "aider":
            result = self._run_aider(work_dir, prompt, error_file)
        else:
            result = self._run_gemini(work_dir, prompt)
        duration_ms = (time.time() - start_time) * 1000

        # Parse result
        success = result.get("error") is None
        tokens_used = self._extract_tokens(result)
        tool_calls = self._extract_tool_calls(result)

        # Verify the fix
        verification_passed = False
        if success:
            verification_passed = self._verify_fix(work_dir, error_file)

        return TestResult(
            case_id=case_id,
            error_type=error_type,
            success=success and verification_passed,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            tool_calls=tool_calls,
            error_message=result.get("error", {}).get("message") if not success else None,
            fix_applied=success,
            verification_passed=verification_passed,
            gemini_response=result.get("response", ""),
            raw_output=result,
        )

    def _capture_python_error(self, work_dir: Path, error_file: str) -> str:
        """Run the Python file and capture the error."""
        try:
            result = subprocess.run(
                [sys.executable, error_file],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stderr or result.stdout
        except subprocess.TimeoutExpired:
            return "Timeout: Script took too long to execute"
        except Exception as e:
            return str(e)

    def _build_fix_prompt(
        self, work_dir: Path, error_file: str, error_output: str, metadata: dict
    ) -> str:
        """Build the prompt for Gemini to fix the error."""
        # Read the error file content
        with open(work_dir / error_file) as f:
            code_content = f.read()

        prompt = f"""Fix the following Python error. This is a cross-file error that requires looking at other files in the project.

## Error Output
```
{error_output}
```

## File: {error_file}
```python
{code_content}
```

## Instructions
1. Analyze the error and identify the root cause
2. Look at other files in the project to understand the correct usage
3. Fix the error in {error_file}
4. Only modify the necessary code to fix the error

Please fix this error."""

        return prompt

    def _run_gemini(self, work_dir: Path, prompt: str) -> dict:
        """Run Gemini CLI and return the JSON result."""
        cmd = [
            self.gemini_cmd,
            prompt,  # Positional argument (--prompt is deprecated)
            "--output-format", "json",
            "--approval-mode", "yolo",  # Auto-approve all actions
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            # Debug: print raw output if verbose
            if os.environ.get("DEBUG"):
                print(f"    [DEBUG] returncode: {result.returncode}")
                print(f"    [DEBUG] stdout length: {len(result.stdout)}")
                print(f"    [DEBUG] stderr: {result.stderr[:200] if result.stderr else 'empty'}")

            # Try to parse JSON from stdout first
            if result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # stdout exists but not valid JSON
                    return {
                        "response": result.stdout,
                        "error": None,
                    }

            # stdout is empty - check if there's an actual error
            # Filter out non-error messages from stderr
            stderr_lines = result.stderr.split('\n') if result.stderr else []
            error_lines = [
                line for line in stderr_lines
                if line.strip() and not any(skip in line for skip in [
                    "YOLO mode is enabled",
                    "StartupProfiler",
                    "INFO",
                    "DEBUG",
                ])
            ]

            if result.returncode != 0 and error_lines:
                return {
                    "error": {
                        "type": "ExecutionError",
                        "message": '\n'.join(error_lines) or f"Exit code: {result.returncode}",
                    }
                }

            # No stdout and no real errors - might be a configuration issue
            return {
                "error": {
                    "type": "NoOutput",
                    "message": "Gemini CLI produced no output. Check if it's properly configured.",
                },
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "error": {
                    "type": "Timeout",
                    "message": f"Gemini CLI timed out after {self.timeout}s",
                }
            }
        except Exception as e:
            return {
                "error": {
                    "type": "Exception",
                    "message": str(e),
                }
            }

    def _run_aider(self, work_dir: Path, prompt: str, error_file: str) -> dict:
        """Run Aider CLI and return the result."""
        # Get all Python files in the work directory
        py_files = list(work_dir.glob("**/*.py"))
        file_args = [str(f.relative_to(work_dir)) for f in py_files]

        cmd = [
            "aider",
            "--model", self.aider_model,
            "--message", prompt,
            "--yes",  # Auto-confirm changes
            "--no-git",  # Don't use git
            "--no-auto-commits",  # Don't auto commit
            "--no-suggest-shell-commands",  # Don't suggest shell commands
            "--no-show-model-warnings",  # Suppress model warnings
        ] + file_args

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if os.environ.get("DEBUG"):
                print(f"    [DEBUG] aider returncode: {result.returncode}")
                print(f"    [DEBUG] stdout length: {len(result.stdout)}")
                print(f"    [DEBUG] stderr: {result.stderr[:500] if result.stderr else 'empty'}")

            # Aider outputs to stdout
            if result.returncode == 0:
                return {
                    "response": result.stdout,
                    "error": None,
                }

            # Check for errors
            error_msg = result.stderr or result.stdout or f"Exit code: {result.returncode}"
            return {
                "error": {
                    "type": "AiderError",
                    "message": error_msg[:500],
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "error": {
                    "type": "Timeout",
                    "message": f"Aider timed out after {self.timeout}s",
                }
            }
        except FileNotFoundError:
            return {
                "error": {
                    "type": "NotFound",
                    "message": "Aider not found. Install with: pip install aider-chat",
                }
            }
        except Exception as e:
            return {
                "error": {
                    "type": "Exception",
                    "message": str(e),
                }
            }

    def _extract_tokens(self, result: dict) -> int:
        """Extract total tokens from Gemini result."""
        stats = result.get("stats", {})
        models = stats.get("models", {})
        total = 0
        for model_stats in models.values():
            tokens = model_stats.get("tokens", {})
            total += tokens.get("total", 0)
        return total

    def _extract_tool_calls(self, result: dict) -> int:
        """Extract total tool calls from Gemini result."""
        stats = result.get("stats", {})
        tools = stats.get("tools", {})
        return tools.get("totalCalls", 0)

    def _verify_fix(self, work_dir: Path, error_file: str) -> bool:
        """Verify the fix by running the code again."""
        try:
            result = subprocess.run(
                [sys.executable, error_file],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Success if no error in stderr and exit code is 0
            return result.returncode == 0 and not any(
                err in result.stderr.lower()
                for err in ["error", "exception", "traceback"]
            )
        except Exception:
            return False

    def run_all(self, error_type: Optional[str] = None) -> BenchmarkSummary:
        """Run all test cases and return summary."""
        cases = self.discover_test_cases(error_type)
        print(f"Discovered {len(cases)} test cases")

        results: list[TestResult] = []

        if self.parallel > 1:
            with ThreadPoolExecutor(max_workers=self.parallel) as executor:
                futures = {
                    executor.submit(self.run_single_test, case): case
                    for case in cases
                }
                for future in as_completed(futures):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        case = futures[future]
                        print(f"  Error running {case.name}: {e}")
        else:
            for case in cases:
                try:
                    results.append(self.run_single_test(case))
                except Exception as e:
                    print(f"  Error running {case.name}: {e}")

        # Build summary
        summary = self._build_summary(results)

        # Save results
        self._save_results(results, summary)

        return summary

    def _build_summary(self, results: list[TestResult]) -> BenchmarkSummary:
        """Build summary from results."""
        if not results:
            return BenchmarkSummary(
                total_cases=0,
                passed=0,
                failed=0,
                success_rate=0.0,
                avg_duration_ms=0.0,
                avg_tokens=0.0,
                timestamp=datetime.now().isoformat(),
            )

        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed

        # Group by error type
        by_error_type = {}
        for r in results:
            if r.error_type not in by_error_type:
                by_error_type[r.error_type] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "avg_duration_ms": 0.0,
                    "avg_tokens": 0.0,
                }
            by_error_type[r.error_type]["total"] += 1
            if r.success:
                by_error_type[r.error_type]["passed"] += 1
            else:
                by_error_type[r.error_type]["failed"] += 1

        # Calculate averages per error type
        for error_type, stats in by_error_type.items():
            type_results = [r for r in results if r.error_type == error_type]
            stats["avg_duration_ms"] = sum(r.duration_ms for r in type_results) / len(type_results)
            stats["avg_tokens"] = sum(r.tokens_used for r in type_results) / len(type_results)
            stats["success_rate"] = stats["passed"] / stats["total"] * 100

        return BenchmarkSummary(
            total_cases=len(results),
            passed=passed,
            failed=failed,
            success_rate=passed / len(results) * 100,
            avg_duration_ms=sum(r.duration_ms for r in results) / len(results),
            avg_tokens=sum(r.tokens_used for r in results) / len(results),
            by_error_type=by_error_type,
            timestamp=datetime.now().isoformat(),
        )

    def _save_results(self, results: list[TestResult], summary: BenchmarkSummary):
        """Save results to JSON files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        results_file = self.results_dir / f"results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)

        # Save summary
        summary_file = self.results_dir / f"summary_{timestamp}.json"
        with open(summary_file, "w") as f:
            json.dump(asdict(summary), f, indent=2)

        print(f"\nResults saved to: {results_file}")
        print(f"Summary saved to: {summary_file}")


def print_summary(summary: BenchmarkSummary):
    """Print formatted summary to console."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Total Cases: {summary.total_cases}")
    print(f"Passed: {summary.passed}")
    print(f"Failed: {summary.failed}")
    print(f"Success Rate: {summary.success_rate:.1f}%")
    print(f"Average Duration: {summary.avg_duration_ms:.0f}ms")
    print(f"Average Tokens: {summary.avg_tokens:.0f}")

    print("\nBy Error Type:")
    print("-" * 60)
    for error_type, stats in summary.by_error_type.items():
        print(f"  {error_type}:")
        print(f"    Success Rate: {stats['success_rate']:.1f}% ({stats['passed']}/{stats['total']})")
        print(f"    Avg Duration: {stats['avg_duration_ms']:.0f}ms")
        print(f"    Avg Tokens: {stats['avg_tokens']:.0f}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run AI CLI benchmark for Python error fixing")
    parser.add_argument(
        "--test-cases-dir",
        default="./test_cases",
        help="Directory containing test cases",
    )
    parser.add_argument(
        "--results-dir",
        default="./results",
        help="Directory to save results",
    )
    parser.add_argument(
        "--error-type",
        choices=["name_error", "import_error", "attribute_error", "type_error", "key_error", "circular_import"],
        help="Run only specific error type",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout for each test case in seconds",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel test runs",
    )
    parser.add_argument(
        "--gemini-cmd",
        default="gemini",
        help="Path to gemini CLI command",
    )
    parser.add_argument(
        "--cli",
        choices=["gemini", "aider"],
        default="gemini",
        help="Which CLI tool to use (gemini or aider)",
    )
    parser.add_argument(
        "--model",
        default="openai/gemini-2.0-flash",
        help="Model to use for aider (e.g., openai/gemini-2.0-flash, gpt-4)",
    )

    args = parser.parse_args()

    print(f"Using CLI tool: {args.cli}")
    if args.cli == "aider":
        print(f"Using model: {args.model}")

    runner = BenchmarkRunner(
        test_cases_dir=args.test_cases_dir,
        results_dir=args.results_dir,
        cli_tool=args.cli,
        gemini_cmd=args.gemini_cmd,
        aider_model=args.model,
        timeout=args.timeout,
        parallel=args.parallel,
    )

    summary = runner.run_all(args.error_type)
    print_summary(summary)


if __name__ == "__main__":
    main()
