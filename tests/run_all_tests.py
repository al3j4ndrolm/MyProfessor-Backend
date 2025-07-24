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

def run_pytest_on_directory(tests_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run pytest on the entire tests directory to discover and run all tests.
    
    Args:
        tests_dir: Path to the tests directory
        verbose: Whether to run in verbose mode
    
    Returns:
        Dictionary with test results
    """
    cmd = ["python", "-m", "pytest", str(tests_dir)]
    
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
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
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
        
        if result["success"]:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        # Print output if verbose
        if args.verbose:
            if result["stdout"]:
                print("\nSTDOUT:")
                print(result["stdout"])
            if result["stderr"]:
                print("\nSTDERR:")
                print(result["stderr"])
        
        return 0 if result["success"] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 