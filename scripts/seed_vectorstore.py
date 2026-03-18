"""Seed the chromeDB vector store from processed document chunks"""

# =============================================================================
# Test: make seed -> ChromeDB vector store populated at data/embeddings/
# =============================================================================

import json
import sys
from pathlib import Path

import structlog

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.logging import setup_logging
from src.retrieval.vectorstore import VectorStore
from src.retrieval.chunking import DocumentChunk
setup_logging()
logger = structlog.get_logger()

PROCESSED_DIR = Path("data/processed")

def load_processed_chunks(processed_dir: Path) -> list:
    """Load all chunked JSON files from processed directory."""
    all_chunks = []
    chunk_files = list(processed_dir.glob("*_chunks.json"))

    if not chunk_files:
        logger.warning(f"No chunk files found in {processed_dir}")
        return []
    
    for file in chunk_files:
        try:
            with file.open('r', encoding='utf-8') as f:
                raw = json.load(f)
                chunks = [DocumentChunk(**cd) for cd in raw]
                all_chunks.extend(chunks)
                logger.info(f"Loaded {len(chunks)} chunks from {file.name}")
        except Exception as e:
            logger.error(f"Error loading chunks from {file.name}: {e}")
            print(f"❌ Error loading {file.name}: {e}")

    return all_chunks

def run_seed() -> None:
    """Embed all processed chunks and store them in chromaDB"""
    print(f"Loading chunks from {PROCESSED_DIR}")
    all_chunks = []
    chunks = load_processed_chunks(PROCESSED_DIR)

    if not chunks:
        print(f"No chunks in {PROCESSED_DIR}")
        print(f"Run `make ingest` to process raw documents into chunks first.")
        return
    
    print(f"Seeding {len(chunks)} chunks to vector store...")
    vs = VectorStore()
    num_added = vs.add_chunks(chunks)
    print(f"✅ Seeded {num_added} chunks to chromaDB collection '{vs._collection.name}'")
    print(f"Total in collection: {vs.count}")

if __name__ == "__main__":
    run_seed()