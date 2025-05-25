#!/usr/bin/env python3
"""
Test Runner for Trustwise Guardrails Framework

This script runs all tests in the tests/ directory.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_test(test_file: str, description: str) -> bool:
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              check=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 TRUSTWISE GUARDRAILS - TEST SUITE")
    print("=" * 60)
    
    # Define tests to run
    tests = [
        ("tests/test_guardrails.py", "Core Guardrails Framework Tests"),
        ("tests/test_adapters.py", "Agent Adapter System Tests"),
        ("tests/test_agent_openai.py", "OpenAI Agent Tests"),
        ("tests/test_agent.py", "AWS Bedrock Agent Tests"),
    ]
    
    # Track results
    passed = 0
    failed = 0
    
    # Run each test
    for test_file, description in tests:
        if os.path.exists(test_file):
            if run_test(test_file, description):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
            failed += 1
    
    # Summary
    total = passed + failed
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n💥 {failed} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 