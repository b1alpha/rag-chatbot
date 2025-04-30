import os

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

persist_dir = "./chroma_store"
source_dir = "./data/sample_docs"


def ingest_documents():
    docs = []
    for fname in os.listdir(source_dir):
        if fname.endswith(".txt"):
            loader = TextLoader(os.path.join(source_dir, fname))
            docs.extend(loader.load())
    # Chroma now handles persistence automatically
    Chroma.from_documents(docs, OpenAIEmbeddings(), persist_directory=persist_dir)


if __name__ == "__main__":
    ingest_documents()
