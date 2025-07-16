# PDF Processing Script for RAG Chatbot

## Overview

This script (`app/process_pdfs.py`) processes PDF documents from the `data/quality_chunks` directory and converts them into reasonably-sized text chunks suitable for use in a RAG (Retrieval-Augmented Generation) system.

## Features

### 1. PDF Text Extraction

- Uses PyMuPDF (fitz) to extract text from PDF files
- Handles multiple pages and preserves document structure
- Includes error handling for corrupted or unreadable PDFs

### 2. Text Cleaning

- Removes HTML tags and excessive whitespace
- Normalizes line breaks and spacing
- Filters out problematic characters while preserving important punctuation
- Ensures consistent text format for embedding

### 3. Intelligent Chunking

- Uses LangChain's `RecursiveCharacterTextSplitter` for optimal chunk creation
- Default chunk size: 1000 characters with 200 character overlap
- Preserves context by splitting at natural boundaries (sentences, paragraphs)
- Configurable chunk size and overlap settings

### 4. Metadata Preservation

- Each chunk includes source PDF filename
- Chunk numbering (e.g., "Chunk: 1/15")
- Metadata headers for better context understanding

### 5. Statistics and Monitoring

- Displays processing progress for each PDF
- Shows chunk creation statistics
- Provides summary of total chunks created
- Calculates average chunk size

## Usage

### Basic Usage

```bash
python app/process_pdfs.py
```

### Configuration

You can modify the following constants in the script:

- `CHUNK_SIZE`: Maximum characters per chunk (default: 1000)
- `CHUNK_OVERLAP`: Characters to overlap between chunks (default: 200)
- `PDF_SOURCE_DIR`: Directory containing PDF files (default: "./data/quality_chunks")
- `OUTPUT_DIR`: Directory for processed text chunks (default: "./data/quality_chunks_processed")

### Output Format

Each chunk is saved as a separate text file with the format:

```
[PDF_NAME]_chunk_[NUMBER].txt
```

Example chunk file content:

```
Source: Document-Name.pdf
Chunk: 1/15
==================================================

[Chunk text content here...]
```

## Integration with RAG System

### Updated Embed Script

The `app/embed.py` script has been enhanced to:

- Process both confluence chunks and PDF chunks
- Load documents from multiple source directories
- Provide progress feedback during ingestion
- Handle missing directories gracefully

### Vector Store Integration

- Processed chunks are automatically ingested into ChromaDB
- Each chunk becomes a separate document in the vector store
- Metadata is preserved for context during retrieval
- Supports semantic search across all document types

## Testing

### Unit Tests

The script includes comprehensive unit tests (`app/tests/test_process_pdfs.py`) that cover:

- Text cleaning functionality
- Chunk creation and sizing
- File saving operations
- Error handling
- PDF extraction (mocked)

### Integration Testing

- Run the full processing pipeline
- Verify chunks are created correctly
- Test RAG system with processed content
- Validate question answering capabilities

## Performance Characteristics

### Processing Statistics (Example)

- **Total PDFs processed**: 5
- **Total chunks created**: 93
- **Average chunk size**: 912 characters
- **Largest document**: 48 chunks (EPS RFC document)
- **Processing time**: ~2-3 seconds per PDF

### Chunk Distribution

- MWAP Test Strategy: 8 chunks
- DigitalQA Testing Terms: 12 chunks
- DigitalQA Culture Change: 15 chunks
- DigitalQA Test Patterns: 10 chunks
- EPS Micro Service Strategy: 48 chunks

## Dependencies

- `PyMuPDF` (fitz): PDF text extraction
- `langchain-text-splitters`: Intelligent text chunking
- `pathlib`: File path operations
- `re`: Regular expressions for text cleaning
- `os`: File system operations

## Error Handling

- Graceful handling of unreadable PDFs
- Skips empty or corrupted files
- Continues processing even if individual files fail
- Provides clear error messages and progress feedback

## Future Enhancements

- Support for different document types (Word, PowerPoint)
- Configurable text cleaning rules
- Advanced metadata extraction
- Parallel processing for large document sets
- Custom chunk sizing based on document type
