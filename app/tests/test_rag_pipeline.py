import pytest
from app.rag_pipeline import get_answer
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_qa_chain():
    with patch('app.rag_pipeline.qa_chain') as mock:
        mock.invoke.return_value = {"result": "This is a test answer"}
        yield mock

def test_get_answer(mock_qa_chain):
    question = "What is this about?"
    answer = get_answer(question)
    
    # Verify the function was called with the correct question
    mock_qa_chain.invoke.assert_called_once_with({"query": question})
    
    # Verify the answer is returned
    assert answer == "This is a test answer"

def test_get_answer_empty_question():
    with pytest.raises(ValueError):
        get_answer("")

def test_get_answer_none_question():
    with pytest.raises(ValueError):
        get_answer(None) 