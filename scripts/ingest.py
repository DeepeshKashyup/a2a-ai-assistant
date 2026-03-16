"""Document ingestion pipeline - read raw files, chunk them, save to processed/"""

# =============================================================================
# Test: make ingest -> data/processed/ contains *_chunks.json files 
# =============================================================================

import sys
from pathlib import Path

# Ensure project root is on that path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import structlog
from src.retrieval.chunking import load_document, chunk_document, save_chunks
from app.core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

def run_ingestion() -> None:
    """Scan RAW_DIR for supported files, load and chunk them, then save to PROCESSED_DIR."""
    files = [
        f for f in RAW_DIR.iterdir() 
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        logger.warning(f"No supported files found in {RAW_DIR}")
        print(f"Add .txt, .pdf, .docx, or .md files to {RAW_DIR} and re-run.")
        return
    
    total_chunks = 0

    for file in files:
        logger.info(f"Processing file: {file.name}")
        try:
            text = load_document(file)
            chunks = chunk_document(text,source_file=str(file))
            output_path = save_chunks(chunks, PROCESSED_DIR)
            total_chunks += len(chunks)
            logger.info(f"Finished processing {file.name}", num_chunks=len(chunks), output_path=str(output_path))
        except Exception as e:
            logger.error(f"Error processing {file.name}: {e}")
            print(f"❌ {file.name}: {e}")

    print(f"\\nIngestion complete: {len(files)} files, {total_chunks} total chunks")

if __name__ == "__main__":
    run_ingestion()