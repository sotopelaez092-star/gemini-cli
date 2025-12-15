#!/usr/bin/env python3
"""
Gemini CLI 跨文件 Bug 修复基准测试

使用方法:
    python run_benchmark.py [--gemini-path /path/to/gemini] [--runs N]

测试指标:
    - 成功率 (Success Rate)
    - 平均修复时间 (Average Fix Time)
    - 迭代轮次 (从日志估算)
"""

import os
import sys
import json
import time
import shutil
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class TestResult:
    """测试结果"""
    case_name: str
    difficulty: str
    files_involved: int
    bug_type: str
    pre_test_failed: bool  # bug 确实存在
    fix_success: bool      # 修复成功
    fix_time_seconds: float
    error_message: Optional[str] = None
    gemini_output: Optional[str] = None

@dataclass
class BenchmarkSummary:
    """基准测试汇总"""
    total_cases: int
    successful_fixes: int
    failed_fixes: int
    success_rate: float
    avg_fix_time_seconds: float
    total_time_seconds: float
    by_difficulty: dict
    results: List[TestResult]

class BenchmarkRunner:
    def __init__(self, gemini_path: str = "gemini", timeout: int = 300):
        self.gemini_path = gemini_path
        self.timeout = timeout
        self.test_cases_dir = Path(__file__).parent / "test_cases"
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)

    def discover_test_cases(self) -> List[Path]:
        """发现所有测试用例"""
        cases = []
        for item in sorted(self.test_cases_dir.iterdir()):
            if item.is_dir() and item.name.startswith("case_"):
                if (item / "test_case.py").exists():
                    cases.append(item)
        return cases

    def parse_bug_description(self, case_dir: Path) -> dict:
        """解析 bug 描述"""
        desc_file = case_dir / "bug_description.txt"
        if not desc_file.exists():
            return {"difficulty": "Unknown", "files_involved": 0, "bug_type": "Unknown"}

        content = desc_file.read_text()
        info = {
            "difficulty": "Unknown",
            "files_involved": 0,
            "bug_type": "Unknown"
        }

        for line in content.split("\n"):
            if line.startswith("Bug Type:"):
                info["bug_type"] = line.split(":", 1)[1].strip()
            elif line.startswith("Difficulty:"):
                info["difficulty"] = line.split(":", 1)[1].strip()
            elif line.startswith("Files Involved:"):
                try:
                    info["files_involved"] = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass

        return info

    def run_test(self, case_dir: Path) -> bool:
        """运行测试用例，返回是否通过"""
        test_file = case_dir / "test_case.py"
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(case_dir)
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def backup_case(self, case_dir: Path) -> Path:
        """备份测试用例"""
        backup_dir = case_dir.parent / f"{case_dir.name}_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(case_dir, backup_dir)
        return backup_dir

    def restore_case(self, case_dir: Path, backup_dir: Path):
        """从备份恢复测试用例"""
        if backup_dir.exists():
            shutil.rmtree(case_dir)
            shutil.copytree(backup_dir, case_dir)
            shutil.rmtree(backup_dir)

    def run_gemini_fix(self, case_dir: Path) -> tuple[bool, float, str]:
        """
        运行 Gemini CLI 修复 bug

        返回: (成功, 耗时, 输出)
        """
        prompt = f"""
Please fix the bug in this Python project.

The test file is test_case.py. Run it first to see the error, then fix the bug.

Rules:
- Only modify the source files, not the test file
- The test should pass after your fix
- Read bug_description.txt for hints about the bug
"""

        start_time = time.time()

        try:
            # 构建命令 - 支持 "node /path/to/gemini.js" 格式
            import shlex
            if self.gemini_path.startswith("node "):
                cmd = f'{self.gemini_path} -y "{prompt}"'
                use_shell = True
            else:
                cmd = [self.gemini_path, "-y", prompt]
                use_shell = False

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(case_dir),
                shell=use_shell
            )
            elapsed = time.time() - start_time

            # 检查修复后测试是否通过
            test_passed = self.run_test(case_dir)

            return test_passed, elapsed, result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            return False, elapsed, "TIMEOUT"
        except FileNotFoundError:
            return False, 0, f"Gemini CLI not found at: {self.gemini_path}"
        except Exception as e:
            return False, 0, str(e)

    def run_single_case(self, case_dir: Path) -> TestResult:
        """运行单个测试用例"""
        case_name = case_dir.name
        bug_info = self.parse_bug_description(case_dir)

        print(f"\n{'='*60}")
        print(f"Testing: {case_name}")
        print(f"Bug Type: {bug_info['bug_type']}")
        print(f"Difficulty: {bug_info['difficulty']}")
        print(f"Files: {bug_info['files_involved']}")
        print(f"{'='*60}")

        # 1. 先验证 bug 存在（测试应该失败）
        print("Step 1: Verifying bug exists...")
        pre_test_result = self.run_test(case_dir)

        if pre_test_result:
            print("  WARNING: Test passed before fix (bug may not exist)")
            return TestResult(
                case_name=case_name,
                difficulty=bug_info["difficulty"],
                files_involved=bug_info["files_involved"],
                bug_type=bug_info["bug_type"],
                pre_test_failed=False,
                fix_success=True,  # Already working
                fix_time_seconds=0,
                error_message="Test already passes, bug may not exist"
            )

        print("  Bug confirmed (test fails as expected)")

        # 2. 备份
        print("Step 2: Creating backup...")
        backup_dir = self.backup_case(case_dir)

        # 3. 运行 Gemini 修复
        print("Step 3: Running Gemini fix...")
        fix_success, fix_time, gemini_output = self.run_gemini_fix(case_dir)

        # 4. 验证修复
        print(f"Step 4: Verifying fix... {'PASS' if fix_success else 'FAIL'}")

        # 5. 恢复备份（保持测试用例原样）
        print("Step 5: Restoring original state...")
        self.restore_case(case_dir, backup_dir)

        result = TestResult(
            case_name=case_name,
            difficulty=bug_info["difficulty"],
            files_involved=bug_info["files_involved"],
            bug_type=bug_info["bug_type"],
            pre_test_failed=True,
            fix_success=fix_success,
            fix_time_seconds=fix_time,
            gemini_output=gemini_output[:2000] if gemini_output else None  # 截断
        )

        print(f"\nResult: {'✓ SUCCESS' if fix_success else '✗ FAILED'}")
        print(f"Time: {fix_time:.2f}s")

        return result

    def run_all(self, runs: int = 1) -> BenchmarkSummary:
        """运行所有测试用例"""
        all_results = []
        cases = self.discover_test_cases()

        print(f"\nFound {len(cases)} test cases")
        print(f"Running {runs} iteration(s) per case")
        print(f"Gemini path: {self.gemini_path}")
        print(f"Timeout: {self.timeout}s per case")

        total_start = time.time()

        for case_dir in cases:
            for run in range(runs):
                if runs > 1:
                    print(f"\n--- Run {run + 1}/{runs} ---")
                result = self.run_single_case(case_dir)
                all_results.append(result)

        total_time = time.time() - total_start

        # 计算汇总
        successful = sum(1 for r in all_results if r.fix_success)
        failed = len(all_results) - successful

        by_difficulty = {}
        for result in all_results:
            diff = result.difficulty
            if diff not in by_difficulty:
                by_difficulty[diff] = {"total": 0, "success": 0}
            by_difficulty[diff]["total"] += 1
            if result.fix_success:
                by_difficulty[diff]["success"] += 1

        for diff in by_difficulty:
            total = by_difficulty[diff]["total"]
            success = by_difficulty[diff]["success"]
            by_difficulty[diff]["rate"] = f"{success/total*100:.1f}%" if total > 0 else "N/A"

        summary = BenchmarkSummary(
            total_cases=len(all_results),
            successful_fixes=successful,
            failed_fixes=failed,
            success_rate=successful / len(all_results) * 100 if all_results else 0,
            avg_fix_time_seconds=sum(r.fix_time_seconds for r in all_results) / len(all_results) if all_results else 0,
            total_time_seconds=total_time,
            by_difficulty=by_difficulty,
            results=all_results
        )

        return summary

    def save_results(self, summary: BenchmarkSummary):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = self.results_dir / f"benchmark_{timestamp}.json"

        # 转换为可序列化格式
        data = {
            "timestamp": timestamp,
            "total_cases": summary.total_cases,
            "successful_fixes": summary.successful_fixes,
            "failed_fixes": summary.failed_fixes,
            "success_rate": f"{summary.success_rate:.1f}%",
            "avg_fix_time_seconds": round(summary.avg_fix_time_seconds, 2),
            "total_time_seconds": round(summary.total_time_seconds, 2),
            "by_difficulty": summary.by_difficulty,
            "results": [asdict(r) for r in summary.results]
        }

        with open(result_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\nResults saved to: {result_file}")
        return result_file

    def print_summary(self, summary: BenchmarkSummary):
        """打印汇总"""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Total Cases:       {summary.total_cases}")
        print(f"Successful Fixes:  {summary.successful_fixes}")
        print(f"Failed Fixes:      {summary.failed_fixes}")
        print(f"Success Rate:      {summary.success_rate:.1f}%")
        print(f"Avg Fix Time:      {summary.avg_fix_time_seconds:.2f}s")
        print(f"Total Time:        {summary.total_time_seconds:.2f}s")

        print("\nBy Difficulty:")
        for diff, stats in sorted(summary.by_difficulty.items()):
            print(f"  {diff}: {stats['success']}/{stats['total']} ({stats['rate']})")

        print("\nDetailed Results:")
        for result in summary.results:
            status = "✓" if result.fix_success else "✗"
            print(f"  {status} {result.case_name} ({result.difficulty}) - {result.fix_time_seconds:.1f}s")


def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Bug Fix Benchmark")
    parser.add_argument("--gemini-path", default="gemini", help="Path to gemini CLI")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs per case")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per case in seconds")
    parser.add_argument("--verify-only", action="store_true", help="Only verify bugs exist, don't run fixes")

    args = parser.parse_args()

    runner = BenchmarkRunner(
        gemini_path=args.gemini_path,
        timeout=args.timeout
    )

    if args.verify_only:
        print("Verifying test cases (bug existence check)...\n")
        cases = runner.discover_test_cases()
        for case_dir in cases:
            bug_info = runner.parse_bug_description(case_dir)
            test_passed = runner.run_test(case_dir)
            status = "✗ FAIL (bug exists)" if not test_passed else "✓ PASS (no bug?)"
            print(f"{case_dir.name}: {status} [{bug_info['difficulty']}]")
        return

    summary = runner.run_all(runs=args.runs)
    runner.print_summary(summary)
    runner.save_results(summary)


if __name__ == "__main__":
    main()
