#!/usr/bin/env python3
"""Simple test to verify PyFix integration works."""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from run_benchmark import BenchmarkRunner


def test_pyfix_integration():
    """Test if PyFix can be called and fix a simple error."""

    # Create a temp directory with a buggy file
    temp_dir = Path(tempfile.mkdtemp(prefix="pyfix_test_"))

    try:
        # Create a simple buggy Python file
        buggy_code = '''
# This file has a NameError bug
def greet(name):
    return "Hello, " + nmae  # Bug: 'nmae' should be 'name'

if __name__ == "__main__":
    print(greet("World"))
'''

        main_file = temp_dir / "main.py"
        main_file.write_text(buggy_code)

        print(f"Test directory: {temp_dir}")
        print(f"Created buggy file: {main_file}")
        print()

        # Check which mode will be used
        pyfix_path = os.environ.get("PYFIX_PATH")
        if pyfix_path:
            print(f"Mode: Direct import (PYFIX_PATH={pyfix_path})")
        else:
            print("Mode: CLI subprocess (pyfix command)")
        print()

        # Create a minimal runner
        runner = BenchmarkRunner(
            test_cases_dir=str(temp_dir),
            results_dir=str(temp_dir / "results"),
            cli_tool="pyfix",
            timeout=60,
        )

        # Try to run the debug agent
        print("Running PyFix...")
        result = runner._run_debugagent(temp_dir, "Fix the bug")

        print()
        print("=" * 50)
        print("RESULT:")
        print("=" * 50)

        if result.get("error"):
            print(f"❌ Error: {result['error']['type']}")
            print(f"   Message: {result['error']['message']}")
            return False
        else:
            print("✅ Success!")
            print(f"Response preview: {result.get('response', '')[:200]}...")

            # Check if file was actually modified
            new_content = main_file.read_text()
            if "name" in new_content and "nmae" not in new_content:
                print("✅ Bug appears to be fixed!")
            else:
                print("⚠️  File may not have been modified correctly")
                print(f"New content:\n{new_content}")

            return True

    finally:
        # Cleanup
        print()
        print(f"Cleaning up: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 50)
    print("PyFix Integration Test")
    print("=" * 50)
    print()

    # Show usage
    print("Usage:")
    print("  Method 1 (CLI):    python test_pyfix.py")
    print("  Method 2 (Import): PYFIX_PATH=/path/to/debug-agent python test_pyfix.py")
    print()

    success = test_pyfix_integration()
    sys.exit(0 if success else 1)
