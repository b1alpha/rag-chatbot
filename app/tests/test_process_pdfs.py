import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from app.process_pdfs import clean_text, create_chunks, save_chunks, extract_text_from_pdf


@pytest.mark.unit
def test_clean_text():
    """Test text cleaning functionality."""
    # Test basic cleaning
    dirty_text = "This  is   a\n\ntest   with   lots\nof  spaces"
    clean = clean_text(dirty_text)
    assert clean == "This is a test with lots of spaces"
    
    # Test HTML/special character removal
    html_text = "This <tag>is</tag> a test with weird chars: ñ@#$%^&*"
    clean = clean_text(html_text)
    # Should remove HTML tags but keep some special chars
    assert "<tag>" not in clean
    assert "</tag>" not in clean
    assert "is" in clean


@pytest.mark.unit
def test_create_chunks():
    """Test text chunking functionality."""
    text = "This is a long text. " * 100  # Create a long text
    chunks = create_chunks(text, chunk_size=200, chunk_overlap=50)
    
    assert len(chunks) > 1  # Should create multiple chunks
    assert all(len(chunk) <= 250 for chunk in chunks)  # Chunks should be reasonable size
    assert len(chunks[0]) > 0  # First chunk should have content


@pytest.mark.unit
def test_save_chunks():
    """Test saving chunks to files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        chunks = ["First chunk content", "Second chunk content"]
        pdf_filename = "test.pdf"
        
        save_chunks(chunks, pdf_filename, tmp_dir)
        
        # Check that files were created
        expected_files = [
            "test_chunk_001.txt",
            "test_chunk_002.txt"
        ]
        
        for expected_file in expected_files:
            file_path = os.path.join(tmp_dir, expected_file)
            assert os.path.exists(file_path)
            
            # Check file content
            with open(file_path, 'r') as f:
                content = f.read()
                assert "Source: test.pdf" in content
                assert "Chunk:" in content


@pytest.mark.unit
def test_extract_text_from_pdf():
    """Test PDF text extraction (mocked)."""
    with patch('app.process_pdfs.fitz.open') as mock_open:
        # Mock the PDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF text content"
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_doc
        
        # Test the function
        result = extract_text_from_pdf("fake_path.pdf")
        
        assert result == "Sample PDF text content"
        mock_open.assert_called_once_with("fake_path.pdf")


@pytest.mark.unit
def test_extract_text_from_pdf_error():
    """Test PDF text extraction error handling."""
    with patch('app.process_pdfs.fitz.open') as mock_open:
        mock_open.side_effect = Exception("PDF read error")
        
        result = extract_text_from_pdf("fake_path.pdf")
        
        assert result is None
