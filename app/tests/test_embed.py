from unittest.mock import MagicMock, patch

import pytest

from app.embed import ingest_documents


@pytest.fixture
def mock_documents():
    return [
        MagicMock(page_content="Test document 1"),
        MagicMock(page_content="Test document 2"),
    ]


@pytest.fixture
def mock_loader():
    with patch("app.embed.TextLoader") as mock_loader:
        mock_doc = MagicMock()
        mock_doc.load.return_value = [MagicMock(page_content="Test content")]
        mock_loader.return_value = mock_doc
        yield mock_loader


@pytest.fixture
def mock_openai_embeddings():
    with patch("app.embed.OpenAIEmbeddings") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.unit
def test_ingest_documents():
    # Mock os.path.exists to return True for both directories
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        
        # Mock os.listdir to return a test file for both directories
        with patch("os.listdir") as mock_listdir:
            mock_listdir.return_value = ["test.txt"]

            # Mock TextLoader
            with patch("app.embed.TextLoader") as mock_loader:
                mock_doc = MagicMock()
                mock_doc.page_content = "Test content"
                mock_loader.return_value.load.return_value = [mock_doc]

                # Mock OpenAIEmbeddings
                with patch("app.embed.OpenAIEmbeddings") as mock_embeddings:
                    mock_embeddings_instance = MagicMock()
                    mock_embeddings.return_value = mock_embeddings_instance

                    # Mock Chroma
                    with patch("app.embed.Chroma") as mock_chroma:
                        # Call the function
                        ingest_documents()

                        # Verify Chroma was called (it should have 2 documents - one from each directory)
                        mock_chroma.from_documents.assert_called_once()
                        call_args = mock_chroma.from_documents.call_args
                        
                        # Check that we have documents from both directories
                        docs_arg = call_args[0][0]  # First positional argument is the documents list
                        assert len(docs_arg) == 2  # Should have 2 documents (one from each directory)
                        
                        # Check other arguments
                        assert call_args[0][1] == mock_embeddings_instance
                        assert call_args[1]['persist_directory'] == "./chroma_store"
