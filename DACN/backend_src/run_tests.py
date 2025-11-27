#!/usr/bin/env python
"""
Run all tests with coverage report
"""
import sys
import subprocess


def run_tests():
    """Run pytest with coverage"""
    print("=" * 60)
    print("Running Tests with Coverage")
    print("=" * 60)
    
    cmd = [
        "pytest",
        "backend_src/tests/",
        "-v",
        "--cov=backend_src/app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except FileNotFoundError:
        print("ERROR: pytest not found. Install with: pip install pytest pytest-cov")
        return 1


def run_specific_tests():
    """Run specific test modules"""
    test_modules = [
        ("Config Tests", "tests/test_config.py"),
        ("Auth Tests", "tests/test_auth.py"),
        ("Validation Tests", "tests/test_validation.py"),
        ("File Validation Tests", "tests/test_file_validation.py"),
    ]
    
    for name, module in test_modules:
        print(f"\n{'=' * 60}")
        print(f"Running {name}")
        print("=" * 60)
        subprocess.run(["pytest", module, "-v"], check=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--separate":
        run_specific_tests()
    else:
        exit_code = run_tests()
        sys.exit(exit_code)
