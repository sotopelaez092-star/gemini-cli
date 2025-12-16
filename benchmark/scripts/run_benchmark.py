#!/usr/bin/env python3
"""
AI CLI Cross-File Python Debug Benchmark Runner

Supports: Gemini CLI, Aider, Claude Code

Usage:
    python run_benchmark.py [--error-type NAME_ERROR] [--parallel 4] [--timeout 120]
    python run_benchmark.py --cli aider --model openai/gemini-2.0-flash
    python run_benchmark.py --cli claude --timeout 300
"""

import argparse
import ast
import difflib
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class FixQuality:
    """Quality assessment of a code fix - Gating + Scoring framework.

    Hard Gates (must pass or score = 0.0):
    - success: The AI tool ran without errors
    - verification_passed: The fix actually resolves the bug

    Scoring weights (only applied if gates pass):
    - correctness_depth: 35% (root cause fix quality)
    - regression_resistance: 20% (test coverage, edge cases)
    - readability: 15% (clarity, maintainability)
    - change_minimality: 15% (necessary changes only)
    - style_preserved: 10% (lint/format consistency)
    - no_extra_code: 5% (avoid unnecessary complexity)
    """
    # Hard gates (must pass)
    tests_pass: bool = True
    bug_fixed: bool = True
    no_new_risks: bool = True

    # Scoring metrics (0-1 each)
    correctness_depth: float = 1.0  # Root cause vs patch fix
    regression_resistance: float = 1.0  # Test coverage, edge cases
    readability: float = 1.0  # Code clarity
    change_minimality: float = 1.0  # Necessary changes only
    style_preserved: float = 1.0  # Format consistency
    no_extra_code: float = 1.0  # No unnecessary additions

    overall_score: float = 0.0
    analysis: str = ""

    # Metrics
    lines_changed: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    files_modified: int = 0
    functions_modified: int = 0
    ast_nodes_changed: int = 0

    # Legacy field for backwards compatibility
    minimal_changes: float = 1.0
    expected_changes: int = 0


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
    fix_quality: Optional[FixQuality] = None


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
    # Quality metrics (Gating + Scoring framework)
    # Primary metrics (includes all cases, failed = 0.0 score)
    avg_quality_all: float = 0.0  # Main metric - includes failed cases as 0
    avg_quality_success_only: float = 0.0  # Only successful cases
    # Statistics
    std_quality_all: float = 0.0
    min_quality: float = 0.0
    max_quality: float = 0.0
    median_quality_all: float = 0.0
    # Per-metric averages (success-only for detailed breakdown)
    avg_correctness_depth: float = 0.0
    avg_regression_resistance: float = 0.0
    avg_readability: float = 0.0
    avg_change_minimality: float = 0.0
    avg_style_preserved: float = 0.0
    avg_no_extra_code: float = 0.0
    quality_grade: str = ""  # A, B, C, D, F (based on avg_quality_all)
    # Legacy fields for backwards compatibility
    avg_quality_score: float = 0.0  # Alias for avg_quality_all
    avg_minimal_changes: float = 0.0


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
        elif self.cli_tool == "claude":
            result = self._run_claude(work_dir, prompt)
        elif self.cli_tool == "pyfix":
            result = self._run_debugagent(work_dir, prompt)
        else:
            result = self._run_gemini(work_dir, prompt)
        duration_ms = (time.time() - start_time) * 1000

        # Parse result
        success = result.get("error") is None
        tokens_used = self._extract_tokens(result)
        tool_calls = self._extract_tool_calls(result)

        # Verify the fix
        verification_passed = False
        fix_quality = None
        if success:
            verification_passed = self._verify_fix(work_dir, error_file)
            # Evaluate fix quality if verification passed
            if verification_passed:
                fix_quality = self._evaluate_fix_quality(case_dir, work_dir, metadata)

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
            fix_quality=fix_quality,
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

    def _run_claude(self, work_dir: Path, prompt: str) -> dict:
        """Run Claude Code CLI and return the result.

        Claude Code uses a ReAct-like pattern similar to Gemini CLI,
        with iterative tool calling (Read, Edit, Bash, etc.).
        """
        cmd = [
            "claude",
            "--print",  # Print response without interactive mode
            "--dangerously-skip-permissions",  # Auto-approve all actions
            prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if os.environ.get("DEBUG"):
                print(f"    [DEBUG] claude returncode: {result.returncode}")
                print(f"    [DEBUG] stdout length: {len(result.stdout)}")
                print(f"    [DEBUG] stderr: {result.stderr[:500] if result.stderr else 'empty'}")

            # Claude outputs to stdout
            if result.returncode == 0:
                return {
                    "response": result.stdout,
                    "error": None,
                }

            # Check for errors
            error_msg = result.stderr or result.stdout or f"Exit code: {result.returncode}"
            return {
                "error": {
                    "type": "ClaudeError",
                    "message": error_msg[:500],
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "error": {
                    "type": "Timeout",
                    "message": f"Claude Code timed out after {self.timeout}s",
                }
            }
        except FileNotFoundError:
            return {
                "error": {
                    "type": "NotFound",
                    "message": "Claude Code not found. Install from: https://github.com/anthropics/claude-code",
                }
            }
        except Exception as e:
            return {
                "error": {
                    "type": "Exception",
                    "message": str(e),
                }
            }

    def _run_debugagent(self, work_dir: Path, prompt: str) -> dict:
        """Run PyFix debug agent.

        PyFix is a custom debug agent that analyzes Python errors
        and applies fixes automatically.
        """
        # Find the main file to fix
        py_files = list(work_dir.glob("*.py"))
        if not py_files:
            return {"error": {"type": "NoFile", "message": "No Python files found"}}

        main_file = work_dir / "main.py" if (work_dir / "main.py").exists() else py_files[0]

        try:
            result = subprocess.run(
                ["pyfix", str(main_file)],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if os.environ.get("DEBUG"):
                print(f"    [DEBUG] pyfix returncode: {result.returncode}")
                print(f"    [DEBUG] stdout length: {len(result.stdout)}")
                print(f"    [DEBUG] stderr: {result.stderr[:500] if result.stderr else 'empty'}")

            # Check for success indicator in output
            success = "✅" in result.stdout or result.returncode == 0

            if success:
                return {
                    "response": result.stdout,
                    "error": None,
                }

            return {
                "error": {
                    "type": "FixFailed",
                    "message": result.stderr or result.stdout or f"Exit code: {result.returncode}",
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "error": {
                    "type": "Timeout",
                    "message": f"PyFix timed out after {self.timeout}s",
                }
            }
        except FileNotFoundError:
            return {
                "error": {
                    "type": "NotFound",
                    "message": "PyFix not found. Make sure 'pyfix' command is in PATH.",
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

    def _evaluate_fix_quality(
        self, case_dir: Path, work_dir: Path, metadata: dict
    ) -> FixQuality:
        """Evaluate the quality of the fix using improved Gating + Scoring framework.

        Gating (hard requirements):
        - tests_pass: Existing tests still pass
        - bug_fixed: The original bug is resolved
        - no_new_risks: No obvious new issues introduced

        Scoring (weighted):
        - correctness_depth (30%): Root cause fix vs superficial patch
        - regression_resistance (20%): Edge case handling, defensive code
        - readability (20%): Code clarity and maintainability
        - change_minimality (15%): Necessary changes only (AST-based)
        - style_preserved (10%): Format/lint consistency
        - no_extra_code (5%): Avoid unnecessary complexity
        """
        quality = FixQuality()
        analysis_parts = []

        # Collect metrics
        lines_added = 0
        lines_removed = 0
        files_modified = 0
        functions_modified = 0
        ast_nodes_changed = 0
        all_diffs = []

        py_files = list(case_dir.glob("**/*.py"))
        for orig_file in py_files:
            rel_path = orig_file.relative_to(case_dir)
            fixed_file = work_dir / rel_path

            if not fixed_file.exists():
                lines_removed += len(orig_file.read_text().splitlines())
                files_modified += 1
                continue

            orig_text = orig_file.read_text()
            fixed_text = fixed_file.read_text()
            orig_lines = orig_text.splitlines(keepends=True)
            fixed_lines = fixed_text.splitlines(keepends=True)

            # Line-based diff
            diff = list(difflib.unified_diff(orig_lines, fixed_lines, lineterm=''))
            if diff:
                files_modified += 1
                all_diffs.append(f"File: {rel_path}\n" + ''.join(diff))

            for line in diff:
                if line.startswith('+') and not line.startswith('+++'):
                    lines_added += 1
                elif line.startswith('-') and not line.startswith('---'):
                    lines_removed += 1

            # AST-based analysis
            try:
                orig_ast = ast.parse(orig_text)
                fixed_ast = ast.parse(fixed_text)
                ast_diff = self._compare_ast(orig_ast, fixed_ast)
                ast_nodes_changed += ast_diff['nodes_changed']
                functions_modified += ast_diff['functions_changed']
            except SyntaxError:
                # If AST parsing fails, the code might be invalid
                pass

        # Check for new files
        for fixed_file in work_dir.glob("**/*.py"):
            rel_path = fixed_file.relative_to(work_dir)
            orig_file = case_dir / rel_path
            if not orig_file.exists():
                lines_added += len(fixed_file.read_text().splitlines())
                files_modified += 1

        lines_changed = lines_added + lines_removed

        # Store metrics
        quality.lines_changed = lines_changed
        quality.lines_added = lines_added
        quality.lines_removed = lines_removed
        quality.files_modified = files_modified
        quality.functions_modified = functions_modified
        quality.ast_nodes_changed = ast_nodes_changed

        # === SCORING ===

        # 1. Correctness Depth (30%): Infer from fix pattern
        # Higher score for targeted fixes, lower for broad changes
        quality.correctness_depth = self._assess_correctness_depth(
            case_dir, work_dir, metadata, ast_nodes_changed, functions_modified
        )

        # 2. Regression Resistance (20%): Check for defensive patterns
        quality.regression_resistance = self._assess_regression_resistance(
            case_dir, work_dir
        )

        # 3. Readability (20%): Code clarity assessment
        quality.readability = self._assess_readability(case_dir, work_dir)

        # 4. Change Minimality (15%): Based on AST changes, not line count
        # Use AST nodes changed instead of expected_lines_to_change
        if ast_nodes_changed == 0:
            quality.change_minimality = 1.0
        elif ast_nodes_changed <= 3:
            quality.change_minimality = 0.95
        elif ast_nodes_changed <= 5:
            quality.change_minimality = 0.85
        elif ast_nodes_changed <= 10:
            quality.change_minimality = 0.7
        elif ast_nodes_changed <= 20:
            quality.change_minimality = 0.5
        else:
            quality.change_minimality = max(0.2, 1.0 - ast_nodes_changed * 0.02)

        # Penalize modifying too many files
        if files_modified > 3:
            quality.change_minimality *= 0.8
        if files_modified > 5:
            quality.change_minimality *= 0.7

        # 5. Style Preserved (10%)
        quality.style_preserved = self._check_style_preservation(case_dir, work_dir)

        # 6. No Extra Code (5%)
        extra_penalty = self._check_extra_code(case_dir, work_dir)
        quality.no_extra_code = max(0.0, 1.0 - extra_penalty)

        # Legacy field
        quality.minimal_changes = quality.change_minimality

        # === CALCULATE OVERALL SCORE ===
        # Weights: correctness(35%) + regression(20%) + readability(15%)
        #        + minimality(15%) + style(10%) + no_extra(5%)
        quality.overall_score = (
            quality.correctness_depth * 0.35 +
            quality.regression_resistance * 0.20 +
            quality.readability * 0.15 +
            quality.change_minimality * 0.15 +
            quality.style_preserved * 0.10 +
            quality.no_extra_code * 0.05
        )
        # Clip to [0, 1] range
        quality.overall_score = max(0.0, min(1.0, quality.overall_score))

        # Build analysis
        if quality.overall_score >= 0.9:
            analysis_parts.append("Excellent fix quality")
        elif quality.overall_score >= 0.75:
            analysis_parts.append("Good fix quality")
        elif quality.overall_score >= 0.6:
            analysis_parts.append("Acceptable fix quality")
        else:
            analysis_parts.append("Needs improvement")

        analysis_parts.append(
            f"AST nodes: {ast_nodes_changed}, "
            f"Files: {files_modified}, "
            f"Funcs: {functions_modified}"
        )

        if all_diffs:
            diff_preview = "\n".join(all_diffs)[:500]
            analysis_parts.append(f"\nDiff preview:\n{diff_preview}")

        quality.analysis = "; ".join(analysis_parts)
        return quality

    def _compare_ast(self, orig_ast: ast.AST, fixed_ast: ast.AST) -> dict:
        """Compare two ASTs and return change metrics."""
        result = {'nodes_changed': 0, 'functions_changed': 0}

        # Get function definitions
        orig_funcs = {node.name: ast.dump(node) for node in ast.walk(orig_ast)
                      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        fixed_funcs = {node.name: ast.dump(node) for node in ast.walk(fixed_ast)
                       if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

        # Count changed functions
        for name, dump in fixed_funcs.items():
            if name not in orig_funcs or orig_funcs[name] != dump:
                result['functions_changed'] += 1

        # Count new/removed functions
        result['functions_changed'] += len(set(orig_funcs.keys()) - set(fixed_funcs.keys()))

        # Rough node count comparison
        orig_nodes = list(ast.walk(orig_ast))
        fixed_nodes = list(ast.walk(fixed_ast))
        result['nodes_changed'] = abs(len(fixed_nodes) - len(orig_nodes))

        return result

    def _assess_correctness_depth(
        self, case_dir: Path, work_dir: Path, metadata: dict,
        ast_nodes_changed: int, functions_modified: int
    ) -> float:
        """Assess if the fix addresses root cause vs superficial patch.

        Higher score for:
        - Targeted, focused changes
        - Changes in the right location (where error originated)
        - Proper error handling vs just suppressing

        Lower score for:
        - Broad scattered changes
        - Exception swallowing
        - Type coercion hacks
        """
        score = 1.0

        for fixed_file in work_dir.glob("**/*.py"):
            try:
                content = fixed_file.read_text()

                # Penalize exception swallowing (bare except, pass in except)
                if 'except:' in content and 'pass' in content:
                    score -= 0.2

                # Penalize broad try/except without specific handling
                if content.count('except Exception') > content.count('except Exception as'):
                    score -= 0.1

                # Penalize type coercion hacks like str(x) or int(x) without validation
                # (This is a heuristic - may need refinement)
                rel_path = fixed_file.relative_to(work_dir)
                orig_file = case_dir / rel_path
                if orig_file.exists():
                    orig_content = orig_file.read_text()
                    # Check if str() or int() was added as a quick fix
                    new_str_calls = content.count('str(') - orig_content.count('str(')
                    new_int_calls = content.count('int(') - orig_content.count('int(')
                    if new_str_calls > 2 or new_int_calls > 2:
                        score -= 0.1

            except Exception:
                pass

        # Bonus for focused changes
        if functions_modified == 1 and ast_nodes_changed <= 5:
            score = min(1.0, score + 0.1)

        return max(0.0, min(1.0, score))

    def _assess_regression_resistance(self, case_dir: Path, work_dir: Path) -> float:
        """Assess if the fix handles edge cases and avoids regressions.

        Higher score for:
        - Proper None/empty checks
        - Type validation
        - Not changing unrelated code

        Lower score for:
        - Removing safety checks
        - Changing function signatures
        - Modifying return types
        """
        score = 1.0

        for fixed_file in work_dir.glob("**/*.py"):
            rel_path = fixed_file.relative_to(work_dir)
            orig_file = case_dir / rel_path

            if not orig_file.exists():
                continue

            try:
                orig_content = orig_file.read_text()
                fixed_content = fixed_file.read_text()

                # Check if safety checks were added (good)
                if fixed_content.count('if ') > orig_content.count('if '):
                    score = min(1.0, score + 0.05)
                if fixed_content.count('is None') > orig_content.count('is None'):
                    score = min(1.0, score + 0.05)
                if fixed_content.count('is not None') > orig_content.count('is not None'):
                    score = min(1.0, score + 0.05)

                # Check if safety checks were removed (bad)
                if fixed_content.count('if ') < orig_content.count('if ') - 1:
                    score -= 0.1
                if fixed_content.count('raise ') < orig_content.count('raise '):
                    score -= 0.05

            except Exception:
                pass

        return max(0.0, min(1.0, score))

    def _assess_readability(self, case_dir: Path, work_dir: Path) -> float:
        """Assess code readability and maintainability.

        Checks:
        - Line length (not too long)
        - Function length (not too long)
        - Nesting depth (not too deep)
        - Clear naming (no single-letter except loop vars)
        """
        score = 1.0

        for fixed_file in work_dir.glob("**/*.py"):
            try:
                lines = fixed_file.read_text().splitlines()

                # Check line length
                long_lines = sum(1 for line in lines if len(line) > 120)
                if long_lines > 0:
                    score -= min(0.1, long_lines * 0.02)

                # Check for very deep nesting (more than 5 levels)
                for line in lines:
                    indent = len(line) - len(line.lstrip())
                    if indent > 20:  # 5 levels * 4 spaces
                        score -= 0.05
                        break

            except Exception:
                pass

        return max(0.0, min(1.0, score))

    def _check_style_preservation(self, case_dir: Path, work_dir: Path) -> float:
        """Check if original code style is preserved."""
        score = 1.0

        for orig_file in case_dir.glob("**/*.py"):
            rel_path = orig_file.relative_to(case_dir)
            fixed_file = work_dir / rel_path

            if not fixed_file.exists():
                continue

            orig_text = orig_file.read_text()
            fixed_text = fixed_file.read_text()

            # Check indentation style (tabs vs spaces)
            orig_uses_tabs = '\t' in orig_text
            fixed_uses_tabs = '\t' in fixed_text
            if orig_uses_tabs != fixed_uses_tabs:
                score -= 0.2

            # Check if quotes style changed significantly
            orig_single = orig_text.count("'")
            orig_double = orig_text.count('"')
            fixed_single = fixed_text.count("'")
            fixed_double = fixed_text.count('"')

            # If original used mostly single quotes but fix uses mostly double (or vice versa)
            if orig_single > orig_double * 2 and fixed_double > fixed_single * 2:
                score -= 0.1
            elif orig_double > orig_single * 2 and fixed_single > fixed_double * 2:
                score -= 0.1

        return max(0.0, score)

    def _check_extra_code(self, case_dir: Path, work_dir: Path) -> float:
        """Check for unnecessary additions like comments, prints, docstrings."""
        penalty = 0.0

        for fixed_file in work_dir.glob("**/*.py"):
            rel_path = fixed_file.relative_to(work_dir)
            orig_file = case_dir / rel_path

            if not orig_file.exists():
                penalty += 0.3  # New file is usually over-engineering
                continue

            orig_lines = orig_file.read_text().splitlines()
            fixed_lines = fixed_file.read_text().splitlines()

            # Count specific patterns
            for line in fixed_lines:
                stripped = line.strip()
                # Check for added debug prints
                if stripped.startswith("print(") and stripped not in [l.strip() for l in orig_lines]:
                    penalty += 0.1
                # Check for added comments that weren't there
                if stripped.startswith("#") and stripped not in [l.strip() for l in orig_lines]:
                    penalty += 0.05

            # Check for added docstrings
            orig_docstrings = orig_file.read_text().count('"""')
            fixed_docstrings = fixed_file.read_text().count('"""')
            if fixed_docstrings > orig_docstrings:
                penalty += 0.1

        return min(1.0, penalty)

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
        """Build summary from results with Gating + Scoring framework.

        Key principle: Failed cases get score = 0.0 (hard gate).
        This ensures avg_quality_all properly reflects both success rate AND fix quality.
        """
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

        # === COMPUTE SCORES FOR ALL CASES ===
        # Hard gate: failed cases get 0.0, successful cases get their quality score
        all_scores = []
        for r in results:
            if not r.success:
                # Hard gate 1: Case failed entirely
                all_scores.append(0.0)
            elif not r.verification_passed:
                # Hard gate 2: Fix didn't actually work
                all_scores.append(0.0)
            elif r.fix_quality is not None:
                # Gates passed, use computed quality score
                all_scores.append(r.fix_quality.overall_score)
            else:
                # Shouldn't happen, but default to 0
                all_scores.append(0.0)

        # Calculate statistics for ALL cases (includes failed as 0)
        avg_quality_all = sum(all_scores) / len(all_scores)
        min_quality = min(all_scores)
        max_quality = max(all_scores)
        median_quality_all = statistics.median(all_scores)
        std_quality_all = statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0

        # Calculate quality metrics for successful fixes only (for detailed breakdown)
        quality_results = [r for r in results if r.fix_quality is not None]
        if quality_results:
            n = len(quality_results)
            avg_quality_success = sum(r.fix_quality.overall_score for r in quality_results) / n
            avg_correctness = sum(r.fix_quality.correctness_depth for r in quality_results) / n
            avg_regression = sum(r.fix_quality.regression_resistance for r in quality_results) / n
            avg_readability = sum(r.fix_quality.readability for r in quality_results) / n
            avg_minimality = sum(r.fix_quality.change_minimality for r in quality_results) / n
            avg_style = sum(r.fix_quality.style_preserved for r in quality_results) / n
            avg_no_extra = sum(r.fix_quality.no_extra_code for r in quality_results) / n
        else:
            avg_quality_success = 0.0
            avg_correctness = 0.0
            avg_regression = 0.0
            avg_readability = 0.0
            avg_minimality = 0.0
            avg_style = 0.0
            avg_no_extra = 0.0

        # Assign grade based on avg_quality_all (the main metric)
        if avg_quality_all >= 0.9:
            grade = "A"
        elif avg_quality_all >= 0.8:
            grade = "B"
        elif avg_quality_all >= 0.7:
            grade = "C"
        elif avg_quality_all >= 0.6:
            grade = "D"
        else:
            grade = "F"

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
                    "avg_quality_all": 0.0,
                    "avg_quality_success_only": 0.0,
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

            # Quality for this error type (all cases, failed = 0)
            type_scores = []
            for r in type_results:
                if not r.success or not r.verification_passed:
                    type_scores.append(0.0)
                elif r.fix_quality is not None:
                    type_scores.append(r.fix_quality.overall_score)
                else:
                    type_scores.append(0.0)
            stats["avg_quality_all"] = sum(type_scores) / len(type_scores)

            # Quality for successful cases only
            type_quality = [r for r in type_results if r.fix_quality is not None]
            if type_quality:
                stats["avg_quality_success_only"] = sum(
                    r.fix_quality.overall_score for r in type_quality
                ) / len(type_quality)
            # Legacy field alias
            stats["avg_quality"] = stats["avg_quality_all"]

        return BenchmarkSummary(
            total_cases=len(results),
            passed=passed,
            failed=failed,
            success_rate=passed / len(results) * 100,
            avg_duration_ms=sum(r.duration_ms for r in results) / len(results),
            avg_tokens=sum(r.tokens_used for r in results) / len(results),
            by_error_type=by_error_type,
            timestamp=datetime.now().isoformat(),
            # Primary quality metrics (Gating + Scoring)
            avg_quality_all=avg_quality_all,
            avg_quality_success_only=avg_quality_success,
            # Statistics
            std_quality_all=std_quality_all,
            min_quality=min_quality,
            max_quality=max_quality,
            median_quality_all=median_quality_all,
            # Per-metric averages (success-only)
            avg_correctness_depth=avg_correctness,
            avg_regression_resistance=avg_regression,
            avg_readability=avg_readability,
            avg_change_minimality=avg_minimality,
            avg_style_preserved=avg_style,
            avg_no_extra_code=avg_no_extra,
            quality_grade=grade,
            # Legacy fields
            avg_quality_score=avg_quality_all,
            avg_minimal_changes=avg_minimality,
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

    # Quality metrics section (Gating + Scoring framework)
    print("\n" + "-" * 60)
    print("FIX QUALITY ASSESSMENT (Gating + Scoring)")
    print("-" * 60)
    print(f"Overall Quality Grade: {summary.quality_grade}")
    print()
    print("Quality Scores:")
    print(f"  avg_quality_all:         {summary.avg_quality_all:.2f} / 1.00  (includes failed=0)")
    print(f"  avg_quality_success_only: {summary.avg_quality_success_only:.2f} / 1.00  (passed cases)")
    print()
    print("Statistics (all cases):")
    print(f"  min: {summary.min_quality:.2f}  max: {summary.max_quality:.2f}  "
          f"median: {summary.median_quality_all:.2f}  std: {summary.std_quality_all:.2f}")
    print()
    print("Scoring Breakdown (success-only, weights in parentheses):")
    print(f"  - Correctness Depth    (35%): {summary.avg_correctness_depth:.2f}")
    print(f"  - Regression Resist.   (20%): {summary.avg_regression_resistance:.2f}")
    print(f"  - Readability          (15%): {summary.avg_readability:.2f}")
    print(f"  - Change Minimality    (15%): {summary.avg_change_minimality:.2f}")
    print(f"  - Style Preserved      (10%): {summary.avg_style_preserved:.2f}")
    print(f"  - No Extra Code         (5%): {summary.avg_no_extra_code:.2f}")

    print("\nBy Error Type:")
    print("-" * 60)
    for error_type, stats in summary.by_error_type.items():
        print(f"  {error_type}:")
        print(f"    Success Rate: {stats['success_rate']:.1f}% ({stats['passed']}/{stats['total']})")
        print(f"    Avg Duration: {stats['avg_duration_ms']:.0f}ms")
        print(f"    Quality (all): {stats.get('avg_quality_all', 0):.2f}  "
              f"(success-only): {stats.get('avg_quality_success_only', 0):.2f}")
    print("=" * 60)


def main():
    # Get the script's directory for relative paths
    script_dir = Path(__file__).parent.parent  # benchmark/ directory

    parser = argparse.ArgumentParser(description="Run AI CLI benchmark for Python error fixing")
    parser.add_argument(
        "--test-cases-dir",
        default=str(script_dir / "test_cases"),
        help="Directory containing test cases",
    )
    parser.add_argument(
        "--results-dir",
        default=str(script_dir / "results"),
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
        default=300,
        help="Timeout for each test case in seconds (default: 300)",
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
        choices=["gemini", "aider", "claude", "pyfix"],
        default="gemini",
        help="Which CLI tool to use (gemini, aider, claude, or pyfix)",
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
