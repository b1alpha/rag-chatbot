import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

persist_dir = "./chroma_store"
confluence_dir = "./data/confluence_chunks"
quality_dir = "./data/quality_chunks_processed"

load_dotenv()


def ingest_documents():
    docs = []
    
    # Process confluence chunks
    if os.path.exists(confluence_dir):
        print(f"Loading confluence documents from {confluence_dir}")
        for fname in os.listdir(confluence_dir):
            if fname.endswith(".txt"):
                loader = TextLoader(os.path.join(confluence_dir, fname))
                docs.extend(loader.load())
        print(f"Loaded {len(docs)} confluence documents")
    
    # Process quality chunks (processed PDFs)
    if os.path.exists(quality_dir):
        print(f"Loading quality documents from {quality_dir}")
        quality_docs = []
        for fname in os.listdir(quality_dir):
            if fname.endswith(".txt"):
                loader = TextLoader(os.path.join(quality_dir, fname))
                quality_docs.extend(loader.load())
        docs.extend(quality_docs)
        print(f"Loaded {len(quality_docs)} quality documents")
    
    if not docs:
        print("No documents found to ingest")
        return
    
    print(f"Total documents to ingest: {len(docs)}")
    
    # Chroma now handles persistence automatically
    Chroma.from_documents(docs, OpenAIEmbeddings(), persist_directory=persist_dir)
    print(f"✅ Documents ingested successfully into {persist_dir}")


if __name__ == "__main__":
    ingest_documents()
