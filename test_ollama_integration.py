#!/usr/bin/env python3
"""
Test script to verify Ollama integration with the RAG system
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rag_pipeline_ollama import test_ollama_connection, get_answer

def main():
    print("🧪 Testing Ollama RAG Integration")
    print("=" * 50)
    
    # Test 1: Check Ollama connection
    print("\n1. Testing Ollama connection...")
    is_working, info = test_ollama_connection()
    
    if is_working:
        print(f"✅ Ollama is running")
        print(f"📋 Available models: {info}")
    else:
        print(f"❌ Ollama connection failed: {info}")
        print("💡 Make sure to run 'ollama serve' first")
        return False
    
    # Test 2: Simple question test
    print("\n2. Testing simple question...")
    try:
        test_question = "What is Python?"
        answer = get_answer(test_question)
        print(f"Question: {test_question}")
        print(f"Answer: {answer[:200]}...")
        print("✅ Simple question test passed")
    except Exception as e:
        print(f"❌ Simple question test failed: {e}")
        return False
    
    # Test 3: RAG-specific question
    print("\n3. Testing RAG-specific question...")
    try:
        rag_question = "What is the ideal test pyramid distribution?"
        answer = get_answer(rag_question)
        print(f"Question: {rag_question}")
        print(f"Answer: {answer[:200]}...")
        print("✅ RAG-specific question test passed")
    except Exception as e:
        print(f"❌ RAG-specific question test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Your Ollama RAG integration is working.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
