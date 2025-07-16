#!/usr/bin/env python3
"""
Simple test of static analysis functionality without API calls
"""

import os
import sys
from pathlib import Path

# Since we're now in the app directory, import directly
from static_analysis import StaticAnalyzer


def test_basic_functionality():
    """Test basic static analysis functionality"""
    
    print("🧪 Testing Static Analysis Basic Functionality")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = StaticAnalyzer()
    
    # Test 1: Test pattern matching
    print("\n1. Testing test pattern matching...")
    test_files = [
        "test_example.py",
        "example.test.js", 
        "component.spec.ts",
        "integration.test.py",
        "e2e.cypress.js",
        "health.check.py"
    ]
    
    for test_file in test_files:
        found_levels = []
        for level_name, patterns in analyzer.test_patterns.items():
            for pattern in patterns:
                if re.search(pattern, test_file, re.IGNORECASE):
                    found_levels.append(level_name)
                    break
        
        print(f"   {test_file} -> {found_levels}")
    
    # Test 2: Test file discovery (using current repo)
    print("\n2. Testing test file discovery...")
    current_repo = "/Volumes/dev/rag-chatbot"
    
    # Mock get_answer to avoid API calls
    def mock_get_answer(question):
        if "unit" in question.lower():
            return "Unit tests verify individual components in isolation"
        elif "integration" in question.lower():
            return "Integration tests verify component interactions"
        elif "e2e" in question.lower():
            return "End-to-end tests verify complete user workflows"
        elif "component" in question.lower():
            return "Component tests verify UI component behavior"
        elif "contract" in question.lower():
            return "Contract tests verify API agreements"
        elif "health" in question.lower():
            return "Health tests verify system monitoring"
        else:
            return "General testing guidance"
    
    # Patch the get_answer function
    import static_analysis
    original_get_answer = static_analysis.get_answer
    static_analysis.get_answer = mock_get_answer
    
    try:
        test_portfolio = analyzer.find_test_files(current_repo)
        
        print("   Test portfolio found:")
        for level_name, level in test_portfolio.items():
            print(f"     {level_name}: {level.count} tests")
            if level.count > 0:
                print(f"       Sample files: {level.files[:3]}")
    
    finally:
        # Restore original function
        static_analysis.get_answer = original_get_answer
    
    # Test 3: CI/CD file detection
    print("\n3. Testing CI/CD file detection...")
    ci_files = analyzer._find_ci_files(current_repo)
    print(f"   Found {len(ci_files)} CI/CD files:")
    for ci_file in ci_files:
        print(f"     {ci_file}")
    
    # Test 4: Documentation file detection
    print("\n4. Testing documentation file detection...")
    doc_files = analyzer._find_documentation_files(current_repo)
    print(f"   Found {len(doc_files)} documentation files:")
    for doc_file in doc_files:
        print(f"     {doc_file}")
    
    # Test 5: Test distribution scoring
    print("\n5. Testing test distribution scoring...")
    test_cases = [
        (70, 20, 10, "Ideal pyramid"),
        (50, 30, 20, "Good distribution"),
        (30, 30, 40, "Inverted pyramid"),
        (10, 10, 80, "Too many E2E tests")
    ]
    
    for unit_pct, integration_pct, e2e_pct, description in test_cases:
        score = analyzer._score_test_distribution(unit_pct, integration_pct, e2e_pct)
        print(f"   {description}: {unit_pct}% unit, {integration_pct}% integration, {e2e_pct}% e2e -> Score: {score}")
    
    print("\n✅ Basic functionality tests completed successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    import re
    test_basic_functionality()
