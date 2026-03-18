"""Document chunking strategies for the ingestion pipeline."""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Literal

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

import structlog
from app.core.config import settings

from src.utils.helpers import hash_text

logger = structlog.get_logger()

@dataclass
class DocumentChunk:
    """chunk of a document with metadata."""

    chunk_id: str
    source_file: str
    text: str
    chunk_index: int
    total_chunks: int
    char_count: int

def load_document(file_path: Path) -> str:
    """Load the content of a document from a file."""

    suffix = file_path.suffix.lower()
    
    if suffix == ".txt" or suffix == ".md":
        return file_path.read_text(encoding="utf-8")
    
    elif suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() for page in reader.pages)
    
    elif suffix == ".docx":
        from docx import Document
        doc = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    
    else:
        logger.error(f"Unsupported file type: {suffix}")
        raise ValueError(f"Unsupported file type: {suffix}")
    
def chunk_document(
            text: str,
            source_file: str,
            strategy: Literal["recursive", "character"] = "recursive",

    ) -> List[DocumentChunk]:
    """Split document text into overlapping chunks
        
        Args:
            text (str): Full text of document.
            source_file (str): The name of the source file for metadata.
            strategy : The chunking strategy to use - recursive(default) or character-based.
        
        Returns :
            List[DocumentChunk]: List of document chunks objects .   
    """   

    if strategy == "character":
        splitter = CharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    raw_chunks = splitter.split_text(text)
    total = len(raw_chunks)

    chunks = [
        DocumentChunk(
            chunk_id=hash_text(f"{source_file}:{i}:{chunk[:50]}"),
            source_file=source_file,
            text=chunk,
            chunk_index=i,
            total_chunks=total,
            char_count=len(chunk)
        ) for i, chunk in enumerate(raw_chunks)
    ]

    logger.info(f"Document chunked into {total} chunks", source_file=source_file, chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    return chunks

def save_chunks(chunks: List[DocumentChunk], output_dir: Path):
    """Save document chunks to JSONL files in the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    source = Path(chunks[0].source_file).stem
    output_path = output_dir / f"{source}_chunks.json"
    
    with output_path.open('w', encoding='utf-8') as f:
        json.dump([asdict(chunk) for chunk in chunks], f, indent=2)

    logger.info(f"Saved {len(chunks)} chunks to {output_path}"
                , output_path=str(output_path), num_chunks=len(chunks))
    return output_path
