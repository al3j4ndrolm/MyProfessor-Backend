#!/usr/bin/env python3
"""
Test Runner Script for MyProfessor Backend

This script uses pytest to automatically discover and run all tests in the repository.
It leverages pytest's built-in test discovery to find and execute all test files.

Usage:
    python tests/run_all_tests.py
    python tests/run_all_tests.py --verbose
    python tests/run_all_tests.py --coverage
    python tests/run_all_tests.py --pattern "test_courses"
"""

import os
import re
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any
import importlib.util
import traceback

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure emoji/unicode output doesn't crash on Windows consoles using cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Matches lines like: tests/foo/test_bar.py::TestClass::test_thing PASSED
_RESULT_LINE_RE = re.compile(
    r"^(?P<nodeid>\S+::\S+)\s+(?P<outcome>PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b"
)
# Matches collection error headers like: ERROR tests/foo/test_bar.py
_COLLECT_ERROR_RE = re.compile(r"^ERROR\s+(?P<nodeid>\S+\.py)\s*$")


def parse_test_results(stdout: str) -> Dict[str, List[str]]:
    """Parse pytest -v output into per-outcome lists of test node ids."""
    results: Dict[str, List[str]] = {
        "PASSED": [], "FAILED": [], "ERROR": [], "SKIPPED": [], "XFAIL": [], "XPASS": [],
    }
    for line in stdout.splitlines():
        match = _RESULT_LINE_RE.match(line.strip())
        if match:
            results[match.group("outcome")].append(match.group("nodeid"))
            continue
        collect_match = _COLLECT_ERROR_RE.match(line.strip())
        if collect_match:
            results["ERROR"].append(f"{collect_match.group('nodeid')} (collection error)")
    return results


def run_pytest_on_directory(tests_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run pytest on the entire tests directory to discover and run all tests.

    Args:
        tests_dir: Path to the tests directory
        verbose: Whether to run in verbose mode

    Returns:
        Dictionary with test results
    """
    # Always run in verbose mode internally so we can parse per-test outcomes,
    # and keep going even if some modules fail to import/collect.
    cmd = ["python", "-m", "pytest", str(tests_dir), "-v", "--continue-on-collection-errors"]

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        end_time = time.time()

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time,
            "results": parse_test_results(result.stdout),
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0,
            "error": True
        }



def run_coverage_tests(tests_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run tests with coverage reporting.
    
    Args:
        tests_dir: Path to the tests directory
        verbose: Whether to run in verbose mode
    
    Returns:
        Coverage results
    """
    try:
        # Check if coverage is installed
        import coverage
    except ImportError:
        print("❌ Coverage not installed. Install with: pip install coverage")
        return {"success": False, "error": "Coverage not installed"}
    
    # Create coverage command
    cmd = ["python", "-m", "coverage", "run", "--source=data_fetchers", "-m", "pytest", str(tests_dir)]
    
    if verbose:
        cmd.append("-v")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        end_time = time.time()
        
        # Generate coverage report
        report_result = subprocess.run(
            ["python", "-m", "coverage", "report"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "coverage_report": report_result.stdout,
            "duration": end_time - start_time
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0,
            "error": True
        }

def print_results(result: Dict[str, Any]) -> None:
    """Print a per-test PASSED/FAILED/ERROR breakdown from a pytest run result."""
    results = result.get("results")
    if not results:
        return

    print(f"\n⏱  Duration: {result['duration']:.2f}s")

    if results["PASSED"]:
        print(f"\n✅ PASSED ({len(results['PASSED'])}):")
        for node_id in results["PASSED"]:
            print(f"   {node_id}")

    if results["FAILED"]:
        print(f"\n❌ FAILED ({len(results['FAILED'])}):")
        for node_id in results["FAILED"]:
            print(f"   {node_id}")

    if results["ERROR"]:
        print(f"\n💥 ERROR ({len(results['ERROR'])}):")
        for node_id in results["ERROR"]:
            print(f"   {node_id}")

    if results["SKIPPED"]:
        print(f"\n⏭  SKIPPED ({len(results['SKIPPED'])}):")
        for node_id in results["SKIPPED"]:
            print(f"   {node_id}")

    total = sum(len(v) for v in results.values())
    print(f"\n📊 Summary: {total} collected — "
          f"{len(results['PASSED'])} passed, "
          f"{len(results['FAILED'])} failed, "
          f"{len(results['ERROR'])} errors, "
          f"{len(results['SKIPPED'])} skipped")


def main():
    """Main function to run all tests."""
    parser = argparse.ArgumentParser(description="Run all tests in the MyProfessor Backend")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--pattern", "-p", help="Test file pattern (e.g., test_*.py, *test.py)")
    parser.add_argument("--framework", "-f", choices=["pytest", "unittest"], 
                       default="pytest", help="Test framework to use (default: pytest)")
    
    args = parser.parse_args()
    
    # Set up tests directory
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    print(f"🔍 Running tests from: {tests_dir.relative_to(project_root)}")
    
    # Build pytest command
    cmd = ["python", "-m", "pytest", str(tests_dir)]
    
    # Add pattern if specified
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    
    # Add verbose flag
    if args.verbose:
        cmd.append("-v")
    
    # Run tests
    print(f"\n🚀 Running tests with {'coverage' if args.coverage else 'standard'} mode...")
    
    if args.coverage:
        # Run with coverage
        coverage_result = run_coverage_tests(tests_dir, args.verbose)
        
        if coverage_result["success"]:
            print("✅ All tests passed with coverage!")
            print("\nCOVERAGE REPORT:")
            print("-" * 40)
            print(coverage_result["coverage_report"])
        else:
            print("❌ Some tests failed!")
            if args.verbose:
                print("STDOUT:", coverage_result["stdout"])
                print("STDERR:", coverage_result["stderr"])
        
        return 0 if coverage_result["success"] else 1
    else:
        # Run standard tests
        result = run_pytest_on_directory(tests_dir, args.verbose)

        # Print output if verbose
        if args.verbose:
            if result["stdout"]:
                print("\nSTDOUT:")
                print(result["stdout"])
            if result["stderr"]:
                print("\nSTDERR:")
                print(result["stderr"])

        print_results(result)

        if result["success"]:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")

        return 0 if result["success"] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 