# Test Suite Documentation

This directory contains the test suite for the MyProfessor Backend project. It includes comprehensive tests for data fetchers, school-specific implementations, and utility functions.

### 1. Main Test Runner (`run_all_tests.py`)

The main test runner uses pytest's built-in discovery to automatically find and run all tests in the repository.

```bash
# Run all tests
python tests/run_all_tests.py

# Run with verbose output
python tests/run_all_tests.py --verbose

# Run with coverage reporting
python tests/run_all_tests.py --coverage
```

### 2. School-Specific Test Runner

```bash
# Run tests for all schools
python tests/data_fetchers/schools/tests.py

# Run tests for De Anza College only
python tests/data_fetchers/schools/tests.py --school de_anza_college

# Run tests for San Jose State University only
python tests/data_fetchers/schools/tests.py --school sjsu
```