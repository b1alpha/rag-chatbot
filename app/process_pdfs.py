import os
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import re

# Configuration
PDF_SOURCE_DIR = "./data/quality_chunks"
OUTPUT_DIR = "./data/quality_chunks_processed"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def clean_text(text):
    """Clean and normalize text extracted from PDFs."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove weird characters that might come from PDFs (but keep common punctuation)
    text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>]', '', text)
    # Normalize line breaks
    text = text.replace('\n', ' ')
    # Remove extra spaces
    text = ' '.join(text.split())
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():  # Only add non-empty pages
                    text += page_text + "\n\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None
    
    return clean_text(text)

def create_chunks(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Split text into chunks using LangChain's text splitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks

def save_chunks(chunks, pdf_filename, output_dir):
    """Save chunks to text files."""
    base_name = Path(pdf_filename).stem
    
    for i, chunk in enumerate(chunks):
        # Create a meaningful filename
        chunk_filename = f"{base_name}_chunk_{i+1:03d}.txt"
        output_path = os.path.join(output_dir, chunk_filename)
        
        # Add metadata header to each chunk
        metadata_header = f"Source: {pdf_filename}\nChunk: {i+1}/{len(chunks)}\n" + "="*50 + "\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(metadata_header + chunk)
        
        print(f"Created chunk: {chunk_filename} ({len(chunk)} characters)")

def process_pdfs():
    """Main function to process all PDFs in the source directory."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(PDF_SOURCE_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {PDF_SOURCE_DIR}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    total_chunks = 0
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_SOURCE_DIR, pdf_file)
        print(f"\nProcessing: {pdf_file}")
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"  Skipping {pdf_file} - no text extracted")
            continue
        
        print(f"  Extracted {len(text)} characters from {pdf_file}")
        
        # Create chunks
        chunks = create_chunks(text)
        if not chunks:
            print(f"  No chunks created for {pdf_file}")
            continue
        
        print(f"  Created {len(chunks)} chunks")
        
        # Save chunks
        save_chunks(chunks, pdf_file, OUTPUT_DIR)
        total_chunks += len(chunks)
    
    print(f"\n✅ Processing complete!")
    print(f"Total chunks created: {total_chunks}")
    print(f"Output directory: {OUTPUT_DIR}")

def show_statistics():
    """Show statistics about the processed chunks."""
    if not os.path.exists(OUTPUT_DIR):
        print(f"Output directory {OUTPUT_DIR} does not exist. Run process_pdfs() first.")
        return
    
    chunk_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    
    if not chunk_files:
        print("No chunk files found.")
        return
    
    print(f"\n📊 Chunk Statistics:")
    print(f"Total chunks: {len(chunk_files)}")
    
    # Group by source PDF
    pdf_groups = {}
    for chunk_file in chunk_files:
        # Extract PDF name from chunk filename
        pdf_name = '_'.join(chunk_file.split('_')[:-2]) + '.pdf'
        if pdf_name not in pdf_groups:
            pdf_groups[pdf_name] = []
        pdf_groups[pdf_name].append(chunk_file)
    
    print(f"Source PDFs processed: {len(pdf_groups)}")
    
    # Show chunks per PDF
    for pdf_name, chunks in pdf_groups.items():
        print(f"  {pdf_name}: {len(chunks)} chunks")
    
    # Show average chunk size
    total_chars = 0
    for chunk_file in chunk_files:
        chunk_path = os.path.join(OUTPUT_DIR, chunk_file)
        with open(chunk_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove metadata header for size calculation
            content_lines = content.split('\n')
            if len(content_lines) > 3 and content_lines[2].startswith('='):
                content = '\n'.join(content_lines[3:])
            total_chars += len(content)
    
    avg_size = total_chars / len(chunk_files) if chunk_files else 0
    print(f"Average chunk size: {avg_size:.0f} characters")

if __name__ == "__main__":
    print("🔄 Processing PDFs into chunks...")
    process_pdfs()
    show_statistics()
