from unittest.mock import MagicMock, patch

import pytest

from app.rag_pipeline import get_answer


@pytest.fixture
def mock_chroma():
    with patch("app.rag_pipeline.Chroma") as mock_chroma:
        mock_collection = MagicMock()
        mock_chroma.return_value = mock_collection
        yield mock_collection


@pytest.fixture
def mock_openai():
    with patch("app.rag_pipeline.OpenAIEmbeddings") as mock_embeddings:
        mock_embeddings.return_value = MagicMock()
        yield mock_embeddings


@pytest.fixture
def mock_chat_openai():
    with patch("app.rag_pipeline.ChatOpenAI") as mock_chat:
        mock_chat.return_value = MagicMock()
        yield mock_chat


@pytest.fixture
def mock_qa_chain():
    with patch("app.rag_pipeline.RetrievalQA.from_chain_type") as mock_qa:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"result": "Test answer"}
        mock_qa.return_value = mock_chain
        yield mock_chain


@pytest.fixture
def mock_get_retriever():
    with patch("app.rag_pipeline.get_retriever") as mock:
        mock_retriever = MagicMock()
        mock.return_value = mock_retriever
        yield mock


@pytest.mark.unit
def test_get_answer(
    mock_chroma, mock_openai, mock_chat_openai, mock_qa_chain, mock_get_retriever
):
    question = "What is the capital of France?"
    answer = get_answer(question)
    assert answer == "Test answer"
    mock_qa_chain.invoke.assert_called_once_with({"query": question})


@pytest.mark.unit
def test_get_answer_empty_question(
    mock_chroma, mock_openai, mock_chat_openai, mock_qa_chain, mock_get_retriever
):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        get_answer("")


@pytest.mark.unit
def test_get_answer_none_question(
    mock_chroma, mock_openai, mock_chat_openai, mock_qa_chain, mock_get_retriever
):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        get_answer(None)
