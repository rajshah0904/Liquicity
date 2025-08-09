#!/usr/bin/env python3
"""
Test runner script for the Python backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main test runner function"""
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting Python Backend Test Suite")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider activating your virtual environment first")
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"], 
                      "Installing test dependencies"):
        print("❌ Failed to install test dependencies")
        return 1
    
    # Run linting
    print("\n🔍 Running code linting...")
    lint_success = True
    
    # Run flake8
    if not run_command([sys.executable, "-m", "flake8", "core", "api", "tests", "--max-line-length=100"], 
                      "Flake8 linting"):
        lint_success = False
    
    # Run black check
    if not run_command([sys.executable, "-m", "black", "--check", "core", "api", "tests"], 
                      "Black formatting check"):
        lint_success = False
    
    # Run isort check
    if not run_command([sys.executable, "-m", "isort", "--check-only", "core", "api", "tests"], 
                      "Import sorting check"):
        lint_success = False
    
    if not lint_success:
        print("❌ Linting failed. Fix the issues before running tests.")
        return 1
    
    # Run type checking
    print("\n🔍 Running type checking...")
    if not run_command([sys.executable, "-m", "mypy", "core", "api"], 
                      "Type checking with mypy"):
        print("⚠️  Type checking failed, but continuing with tests...")
    
    # Run unit tests
    print("\n🧪 Running unit tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-m", "unit", "--cov=core", "--cov=api"], 
                      "Unit tests"):
        print("❌ Unit tests failed")
        return 1
    
    # Run security tests
    print("\n🔒 Running security tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-m", "security"], 
                      "Security tests"):
        print("❌ Security tests failed")
        return 1
    
    # Run API tests
    print("\n🌐 Running API tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-m", "api"], 
                      "API tests"):
        print("❌ API tests failed")
        return 1
    
    # Run integration tests (if not marked as slow)
    print("\n🔗 Running integration tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-m", "integration", "-m", "not slow"], 
                      "Integration tests (excluding slow tests)"):
        print("⚠️  Some integration tests failed, but continuing...")
    
    # Run all tests with coverage
    print("\n📊 Running full test suite with coverage...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "--cov=core", "--cov=api", "--cov-report=html", "--cov-report=term-missing"], 
                      "Full test suite with coverage"):
        print("❌ Full test suite failed")
        return 1
    
    print("\n✅ All tests completed successfully!")
    print("📊 Coverage report generated in htmlcov/")
    print("🎉 Test suite passed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 