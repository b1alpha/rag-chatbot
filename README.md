# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that can answer questions based on your custom documents.

## Setup

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

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /query`: Submit a question
  ```json
  {
    "question": "Your question here"
  }
  ```

## Docker Support

Build and run with Docker:
```bash
docker build -t rag-chatbot .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here rag-chatbot
``` 