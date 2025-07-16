#!/usr/bin/env python3
"""
Example usage of the static analysis tool
"""

import os
import sys
from pathlib import Path

# Since we're now in the app directory, import directly
from static_analysis import StaticAnalyzer


def demo_analysis():
    """Demo the static analysis workflow"""
    
    # For demo purposes, let's analyze this repo itself
    current_repo = "/Volumes/dev/rag-chatbot"
    
    print("🚀 Static Analysis Demo")
    print("=" * 50)
    
    print("\n1. Initializing analyzer...")
    analyzer = StaticAnalyzer()
    
    print("\n2. Loading quality context from processed chunks...")
    quality_context = analyzer.load_quality_context()
    print(f"   Loaded {len(quality_context)} characters of quality guidance")
    
    print("\n3. Analyzing test portfolio...")
    test_portfolio = analyzer.find_test_files(current_repo)
    
    for level_name, level in test_portfolio.items():
        if level.count > 0:
            print(f"   Found {level.count} {level_name} tests")
    
    print("\n4. Assessing strategy compliance...")
    strategy_assessment = analyzer.assess_strategy_compliance(current_repo)
    print(f"   Overall compliance score: {strategy_assessment['overall_score']:.1f}/100")
    
    print("\n5. Finding quality issues...")
    quality_issues = analyzer.find_quality_issues(current_repo)
    print(f"   Found {len(quality_issues)} quality issues")
    
    high_severity = [issue for issue in quality_issues if issue.severity == "HIGH"]
    print(f"   High severity issues: {len(high_severity)}")
    
    print("\n6. Generating full report...")
    report = analyzer.generate_report(current_repo)
    
    print("\n7. Displaying report...")
    analyzer.print_report(report)
    
    return report


if __name__ == "__main__":
    demo_analysis()
