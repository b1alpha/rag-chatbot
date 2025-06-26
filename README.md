# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that can answer questions based on your custom documents.

## Overview

This project is designed as a modular and scalable Retrieval-Augmented Generation (RAG) chatbot application. It combines document retrieval with generative AI models to provide accurate and context-aware answers to user queries. Below are the key architectural decisions and components that make up this project.

## FastAPI for Web Framework

FastAPI is chosen as the web framework for this project due to its high performance, ease of use, and modern features. It provides:

- **REST API Endpoints**: The application exposes two main endpoints:
  - `GET /health`: A health check endpoint to verify the server is running.
  - `POST /query`: Accepts a user query and returns an AI-generated response based on the ingested documents.
- **Validation**: FastAPI's built-in validation ensures that incoming requests are properly formatted.
- **Asynchronous Support**: FastAPI supports asynchronous programming, enabling efficient handling of multiple requests.

## LangChain for RAG Pipeline

LangChain is utilized to implement the Retrieval-Augmented Generation (RAG) pipeline. This pipeline combines:

- **Document Retrieval**: LangChain retrieves relevant documents from the vector store based on the user query.
- **Generative AI Models**: It uses OpenAI's chat models to generate responses that are informed by the retrieved documents.

LangChain's modular design allows for easy integration and customization, making it ideal for building complex AI applications.

## Chroma for Vector Store

Chroma is used as the vector store to manage and retrieve document embeddings. Key features include:

- **Persistence**: Chroma supports persistent storage, ensuring that embeddings are retained across application restarts.
- **Efficiency**: It enables fast and accurate retrieval of relevant documents based on user queries.
- **Scalability**: Chroma can handle large datasets, making it suitable for production environments.

## OpenAI Models

OpenAI's models are integrated into the application for two main purposes:

- **Embeddings**: OpenAI's embedding models convert text documents into vector representations, which are stored in Chroma.
- **Generative Responses**: OpenAI's chat models generate answers to user queries, leveraging the context provided by the retrieved documents.

This integration ensures high-quality results and seamless compatibility with LangChain.

## Environment Configuration

The application uses environment variables to manage sensitive information and configuration settings. Key aspects include:

- **.env File**: A `.env` file is used to store the OpenAI API key and other configuration parameters.
- **Security**: Environment variables ensure that sensitive information is not hardcoded into the application.
- **Flexibility**: This approach allows for easy configuration across different environments (e.g., development, testing, production).

## Document Ingestion

A dedicated script (`app/embed.py`) handles the ingestion of documents. The process involves:

1. **Reading Documents**: Text files are read from the `data/sample_docs` directory.
2. **Generating Embeddings**: The script uses OpenAI's embedding models to convert the text into vector representations.
3. **Storing Embeddings**: The generated embeddings are stored in the Chroma vector store for later retrieval.

This modular design ensures that new documents can be easily added to the system.

## Testing Strategy

The project includes a comprehensive testing strategy to ensure reliability and maintainability:

- **Unit Tests**: Located in `app/tests`, these tests validate individual components of the application.
- **Integration Tests**: Found in `app/tests/integration`, these tests verify the end-to-end functionality of the system, including Dockerized deployments.

## Docker for Containerization

The application is containerized using Docker to ensure consistent environments across development, testing, and production. Key benefits include:

- **Portability**: Docker containers can run on any system that supports Docker.
- **Isolation**: Each container runs in its own isolated environment, preventing conflicts between dependencies.
- **Ease of Deployment**: Docker simplifies the deployment process, making it easy to run the application in different environments.

## Pre-commit Hooks

Pre-commit hooks are configured to enforce code quality and formatting standards. Tools used include:

- **Black**: Ensures consistent code formatting.
- **Isort**: Organizes imports in a standardized manner.
- **Pytest**: Runs unit tests to catch errors before code is committed.

## Continuous Integration

CI pipelines are implemented using GitHub Actions and GitLab CI to automate testing and building processes. This ensures:

- **Code Quality**: Automated tests catch issues early in the development process.
- **Consistency**: Builds are tested in a controlled environment, reducing the risk of deployment failures.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)

### Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   Create a `.env` file in the root directory and add:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. Add your documents:
   Place your text documents in the `data/sample_docs` directory.

5. Ingest documents:
   ```bash
   python app/embed.py
   ```

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000

### API Endpoints

- `GET /health`: Health check endpoint
- `POST /query`: Submit a question
  ```json
  {
    "question": "Your question here"
  }
  ```

### Docker Support

Build and run with Docker:

#### Option 1: Using environment variables directly
```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here rag-chatbot
```

#### Option 2: Using a .env file
```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 --env-file .env rag-chatbot
```

Note: Make sure your `.env` file is in the same directory where you run the docker command.
