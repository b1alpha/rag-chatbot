#!/usr/bin/env python3
"""
Simple demo of the static analysis system using Ollama instead of OpenAI
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from static_analysis import StaticAnalyzer

def main():
    print("🎯 RAG-Powered Static Analysis with Ollama")
    print("=" * 50)
    
    # Create analyzer instance with correct path
    analyzer = StaticAnalyzer(quality_chunks_dir="data/quality_chunks_processed")
    
    # Demo 1: Test level description
    print("\n1. Getting test level description from RAG...")
    description = analyzer._get_test_level_description('unit')
    print(f"Unit Test Description: {description[:200]}...")
    
    # Demo 2: Load quality context
    print("\n2. Loading quality context...")
    context = analyzer.load_quality_context()
    print(f"Quality context loaded: {len(context)} characters")
    
    # Demo 3: Test distribution scoring
    print("\n3. Testing distribution scoring...")
    score = analyzer._score_test_distribution(70, 20, 10)
    print(f"Perfect pyramid score (70/20/10): {score}")
    
    bad_score = analyzer._score_test_distribution(10, 10, 80)
    print(f"Poor pyramid score (10/10/80): {bad_score}")
    
    # Demo 4: Simple repository analysis
    print("\n4. Analyzing current repository...")
    repo_path = "/Volumes/dev/rag-chatbot"
    
    if os.path.exists(repo_path):
        print(f"Scanning for tests in: {repo_path}")
        test_portfolio = analyzer.find_test_files(repo_path)
        
        print(f"\nFound {len(test_portfolio)} test levels:")
        for level, info in test_portfolio.items():
            print(f"  {level}: {info.count} tests")
        
        # Get overall analysis
        print("\n5. Getting RAG analysis...")
        question = "What are the key principles of effective test automation?"
        answer = analyzer._get_test_level_description(question)
        print(f"RAG Answer: {answer[:300]}...")
    
    print("\n🎉 Demo completed successfully!")
    print("Your RAG system is now running locally with Ollama!")

if __name__ == "__main__":
    main()
