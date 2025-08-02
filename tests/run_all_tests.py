#!/usr/bin/env python3
"""
Comprehensive test runner for Mind Map Framework

This script runs all unit tests and provides a summary report.
Use this for deployment verification and regression testing.

Usage:
    python run_all_tests.py           # Run all tests
    python run_all_tests.py --verbose # Verbose output
    python run_all_tests.py --module test_docx_creator  # Run specific module
"""

import sys
import os
import pytest
import argparse
from datetime import datetime


class TestRunner:
    """Comprehensive test runner with reporting"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        
    def run_tests(self, verbose=False, specific_module=None):
        """Run all tests or specific module"""
        print("🧪 Mind Map Framework Test Suite")
        print("=" * 50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = datetime.now()
        
        # Change to tests directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(test_dir)
        
        # Prepare pytest arguments
        pytest_args = []
        
        if verbose:
            pytest_args.extend(['-v', '-s'])
        
        if specific_module:
            pytest_args.append(f"test_{specific_module}.py")
        else:
            # Run all test files
            pytest_args.extend([
                'test_docx_creator.py',
                'test_mindmap_core.py', 
                'test_epub_processor.py',
                'test_app_functions.py',
                'test_utils.py'
            ])
        
        # Add coverage and reporting options
        pytest_args.extend([
            '--tb=short',  # Short traceback format
        ])
        
        try:
            # Run tests
            exit_code = pytest.main(pytest_args)
            self.end_time = datetime.now()
            
            # Generate summary
            self._print_summary(exit_code)
            
            return exit_code == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def _print_summary(self, exit_code):
        """Print test summary"""
        duration = self.end_time - self.start_time
        
        print()
        print("📊 Test Summary")
        print("=" * 50)
        print(f"Duration: {duration}")
        print(f"Finished at: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if exit_code == 0:
            print("✅ All tests passed!")
            print()
            print("🚀 System is ready for deployment")
        else:
            print("❌ Some tests failed!")
            print()
            print("🔧 Please fix failing tests before deployment")
        
        print()
        print("📋 Test Modules:")
        print("  • test_docx_creator.py    - DOCX generation and formatting")
        print("  • test_mindmap_core.py    - Mind map generation pipeline")
        print("  • test_epub_processor.py  - EPUB file processing")
        print("  • test_app_functions.py   - Flask app core functions")
        print("  • test_utils.py          - Utility functions")
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking Dependencies...")
        
        required_packages = [
            'pytest',
            'python-docx',
            'requests',
            'flask'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package} (missing)")
                missing.append(package)
        
        if missing:
            print()
            print("⚠️  Missing dependencies. Install with:")
            print(f"conda install {' '.join(missing)}")
            return False
        
        print("✅ All required dependencies available")
        print()
        return True
    
    def setup_test_environment(self):
        """Set up test environment"""
        # Add parent directory to path for imports
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Set environment variables for testing
        os.environ['TESTING'] = 'true'
        os.environ['SKIP_API_CALLS'] = 'true'  # Skip real API calls in tests


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run Mind Map Framework tests')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose test output')
    parser.add_argument('--module', '-m', type=str,
                       help='Run specific test module (e.g., docx_creator)')
    parser.add_argument('--check-deps', action='store_true',
                       help='Only check dependencies')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Set up test environment
    runner.setup_test_environment()
    
    # Check dependencies
    if not runner.check_dependencies():
        return 1
    
    if args.check_deps:
        return 0
    
    # Run tests
    success = runner.run_tests(
        verbose=args.verbose,
        specific_module=args.module
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())