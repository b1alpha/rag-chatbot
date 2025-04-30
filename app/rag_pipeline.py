from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader

persist_dir = "./chroma_store"

retriever = Chroma(
    persist_directory=persist_dir,
    embedding_function=OpenAIEmbeddings()
).as_retriever()

# Specify GPT-3.5 Turbo model
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever
)

def get_answer(question):
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string")
    result = qa_chain.invoke({"query": question})
    return result["result"] 