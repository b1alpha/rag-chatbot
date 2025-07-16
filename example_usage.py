#!/usr/bin/env python3
"""
Simple example of using the Ollama RAG system
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Silence the deprecation warning
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

from rag_pipeline_ollama import get_answer

def main():
    print("🤖 RAG-Powered Q&A with Ollama")
    print("=" * 40)
    
    # Example questions
    questions = [
        "What is unit testing?",
        "What is the ideal test pyramid distribution?",
        "What are the benefits of test automation?",
        "What is continuous integration?",
        "What are the principles of good test design?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 50)
        try:
            answer = get_answer(question)
            # Show first 300 characters
            print(f"Answer: {answer[:300]}...")
        except Exception as e:
            print(f"Error: {e}")
        print()

if __name__ == "__main__":
    main()
