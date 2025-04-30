import pytest
import os
from unittest.mock import patch, MagicMock
from app.embed import ingest_documents

@pytest.fixture
def mock_documents():
    return [
        MagicMock(page_content="Test document 1"),
        MagicMock(page_content="Test document 2")
    ]

@pytest.fixture
def mock_loader():
    with patch('app.embed.TextLoader') as mock:
        instance = mock.return_value
        instance.load.return_value = [MagicMock(page_content="Test document")]
        yield mock

def test_ingest_documents(mock_loader, tmp_path):
    # Create a temporary directory for testing
    test_source_dir = tmp_path / "test_docs"
    test_source_dir.mkdir()
    test_persist_dir = tmp_path / "test_chroma"
    
    # Create a test file
    test_file = test_source_dir / "test.txt"
    test_file.write_text("Test content")
    
    with patch('app.embed.source_dir', str(test_source_dir)), \
         patch('app.embed.persist_dir', str(test_persist_dir)), \
         patch('app.embed.Chroma.from_documents') as mock_chroma:
        
        ingest_documents()
        
        # Verify TextLoader was called with the correct path
        mock_loader.assert_called_once_with(str(test_file))
        
        # Verify Chroma.from_documents was called
        mock_chroma.assert_called_once() 