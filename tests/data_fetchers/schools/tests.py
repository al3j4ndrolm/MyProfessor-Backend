#!/usr/bin/env python3
"""
School Test Runner Script for MyProfessor Backend

This script runs tests for specific schools or all schools in the repository.
It provides a convenient way to test individual school implementations.

Usage:
    python tests/data_fetchers/schools/tests.py                    # Run all school tests
    python tests/data_fetchers/schools/tests.py --school de_anza   # Run De Anza tests only
    python tests/data_fetchers/schools/tests.py --school sjsu      # Run SJSU tests only
    python tests/data_fetchers/schools/tests.py --verbose          # Verbose output
    python tests/data_fetchers/schools/tests.py --list-schools     # List available schools
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def get_available_schools() -> Dict[str, str]:
    """
    Get a mapping of school codes to their full names.
    
    Returns:
        Dictionary mapping school codes to full names
    """
    return {
        "de_anza_college": "De Anza College",
        "sjsu": "San Jose State University",
        "foothill": "Foothill College",
        "sfsu": "San Francisco State University"
    }

def find_school_test_files(school_code: Optional[str] = None) -> List[Path]:
    """
    Find test files for a specific school or all schools.
    
    Args:
        school_code: School code to filter by (None for all schools)
    
    Returns:
        List of Path objects for test files
    """
    schools_dir = project_root / "tests" / "data_fetchers" / "schools"
    test_files = []
    
    if school_code:
        # Look for specific school
        school_dir = schools_dir / school_code
        if not school_dir.exists():
            print(f"❌ School directory not found: {school_dir}")
            return []
        
        # Find test files in this school's directory
        for file in school_dir.glob("test_*.py"):
            test_files.append(file)
    else:
        # Find test files in all school directories
        for school_dir in schools_dir.iterdir():
            if school_dir.is_dir() and not school_dir.name.startswith("__"):
                for file in school_dir.glob("test_*.py"):
                    test_files.append(file)
    
    return sorted(test_files)

def run_pytest_on_file(test_file: Path, verbose: bool = False) -> Dict[str, Any]:
    """
    Run pytest on a single test file.
    
    Args:
        test_file: Path to the test file
        verbose: Whether to run in verbose mode
    
    Returns:
        Dictionary with test results
    """
    cmd = ["python", "-m", "pytest", str(test_file)]
    
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
            "file": test_file,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": end_time - start_time
        }
    except Exception as e:
        return {
            "file": test_file,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration": 0,
            "error": True
        }

def run_school_tests(school_code: Optional[str], verbose: bool = False):
    """
    Run tests for a specific school or all schools.
    
    Args:
        school_code: School code to test (None for all schools)
        verbose: Whether to run in verbose mode
    
    Returns:
        Dictionary with overall results
    """
    schools = get_available_schools()
    
    if school_code and school_code not in schools:
        print(f"❌ Unknown school code: {school_code}")
        print(f"Available schools: {', '.join(schools.keys())}")
        return {"success": False, "error": f"Unknown school: {school_code}"}
    
    # Find test files
    test_files = find_school_test_files(school_code)
    
    if not test_files:
        if school_code:
            print(f"❌ No test files found for school: {school_code}")
        else:
            print("❌ No test files found for any school")
        return {"success": False, "error": "No test files found"}
    
    # Display what we're testing
    if school_code:
        school_name = schools[school_code]
        print(f"🔍 Running tests for {school_name} ({school_code})\n")
        print(f"📋 Found {len(test_files)} test files:")
    else:
        print(f"🔍 Running tests for all schools\n")
        print(f"📋 Found {len(test_files)} test files:")
    
    # Run tests
    results = []
    
    for test_file in test_files:
        result = run_pytest_on_file(test_file, verbose)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {test_file.parent.name} - {test_file.name}")
        else:
            print(f"❌ {test_file.parent.name} - {test_file.name}")
    
    # Print results
    for result in results:
        if not result["success"]:
            print(f"\n--------------------------------Result output--------------------------------")
            if result["stdout"]:
                print("STDOUT:")
                print(result["stdout"])
            if result["stderr"]:
                print("STDERR:")
                print(result["stderr"])

def main():
    """Main function to run school tests."""
    parser = argparse.ArgumentParser(description="Run tests for specific schools in MyProfessor Backend")
    parser.add_argument("--school", "-s", help="School code to test (e.g., de_anza_college, sjsu)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list-schools", "-l", action="store_true", help="List available schools")
    
    args = parser.parse_args()
    
    # List available schools if requested
    if args.list_schools:
        schools = get_available_schools()
        print("Available schools:")
        for code, name in schools.items():
            print(f"  {code}: {name}")
        return 0
    
    # Run tests
    run_school_tests(args.school, args.verbose)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 