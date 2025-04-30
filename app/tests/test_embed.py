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
    # Mock os.listdir to return a test file
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

                    # Verify Chroma was called with correct arguments
                    mock_chroma.from_documents.assert_called_once_with(
                        [mock_doc],
                        mock_embeddings_instance,
                        persist_directory="./chroma_store",
                    )
