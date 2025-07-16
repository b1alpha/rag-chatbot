from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings  # Still using OpenAI for embeddings
from langchain_ollama import ChatOllama
import requests
import json

load_dotenv()


def get_retriever():
    persist_dir = "./chroma_store"
    return Chroma(persist_directory=persist_dir, embedding_function=OpenAIEmbeddings())


def get_answer_ollama(question: str, model_name: str = "llama3.2:1b") -> str:
    """
    Get answer using local Ollama model instead of OpenAI API.
    This version uses direct API calls to Ollama for more control.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:
        # Get relevant context from vector store
        retriever = get_retriever()
        docs = retriever.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        # Create prompt with context
        prompt = f"""Context: {context}

Question: {question}

Please provide a comprehensive answer based on the context provided above."""

        # Call Ollama API directly
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response generated')
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error connecting to local model: {str(e)}"


def get_answer_ollama_langchain(question: str, model_name: str = "llama3.2:1b") -> str:
    """
    Get answer using Ollama through LangChain integration.
    This version uses the LangChain Ollama wrapper.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:
        retriever = get_retriever()
        
        # Create Ollama LLM instance
        llm = ChatOllama(
            model=model_name,
            temperature=0.3,
            base_url="http://localhost:11434"
        )
        
        # Create QA chain with Ollama
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type="stuff", 
            retriever=retriever.as_retriever()
        )

        result = qa_chain.invoke({"query": question})
        return result["result"]
        
    except Exception as e:
        return f"Error with Ollama LangChain integration: {str(e)}"


# Default function - uses direct API approach
def get_answer(question: str) -> str:
    """
    Default get_answer function that uses Ollama instead of OpenAI.
    This is a drop-in replacement for the original function.
    """
    return get_answer_ollama(question)


# Test function to check if Ollama is working
def test_ollama_connection():
    """Test if Ollama service is running and responsive"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            return True, available_models
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    # Test the connection
    is_working, info = test_ollama_connection()
    print(f"Ollama connection: {'✓' if is_working else '✗'}")
    print(f"Info: {info}")
    
    if is_working:
        # Test a simple question
        test_question = "What is unit testing?"
        print(f"\nTesting question: {test_question}")
        answer = get_answer(test_question)
        print(f"Answer: {answer}")
