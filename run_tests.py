#!/usr/bin/env python3
"""
Test runner for DAT Score Calculator web application.
"""
import sys
import os
import pytest

def main():
    """Run the test suite."""
    print("🧪 Running DAT Score Calculator Tests...")
    print("=" * 50)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests with verbose output
    args = [
        'test_main.py',
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings',  # Disable warnings for cleaner output
    ]
    
    # Add coverage if available
    try:
        import coverage  # type: ignore
        args.extend(['--cov=main', '--cov-report=term-missing'])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("ℹ️  Coverage not available (install with: pip install coverage)")
    
    # Run the tests
    exit_code = pytest.main(args)
    
    print("=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main()) 