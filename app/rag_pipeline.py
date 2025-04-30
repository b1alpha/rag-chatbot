from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()


def get_retriever():
    persist_dir = "./chroma_store"
    return Chroma(persist_directory=persist_dir, embedding_function=OpenAIEmbeddings())


def get_answer(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    retriever = get_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(), chain_type="stuff", retriever=retriever.as_retriever()
    )

    result = qa_chain.invoke({"query": question})
    return result["result"]
