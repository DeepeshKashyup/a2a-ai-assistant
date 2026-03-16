###ChromaDB vector store operations: store, query, delete. 

# =============================================================================
# Test: make seed -> ChromeDB vector store populated at data/embeddings/
# =============================================================================

from dataclasses import dataclass
from typing import Optional

import chromadb
import structlog
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings
from src.retrieval.chunking import DocumentChunk
from src.retrieval.embeddings import EmbeddingClient

logger = structlog.get_logger()

@dataclass
class SearchResult:
    """A single similarity search result with content and metadata."""
    chunk_id: str
    text: str
    source_file: str
    score: float
    chunk_index: int

class VectorStore:
    """ChromaDB-backed vector store for document chunks."""

    def __init__(self) -> None:
        self._embedder = EmbeddingClient()
        self._client = chromadb.PersistentClient(
            path = settings.chroma_persistend_dir,
            settings = ChromaSettings(anonymized_telemetry=False)
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(
            "vector store initialized",
            collection = settings.chroma_collection,
            embedding_model = settings.embedding_model,
            chroma_persistent_dir = settings.chroma_persistend_dir
        )

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        """Embed abd store document chunks in chromaDB
           
            Args:
                chunks (list): List of DocumentChunk objects to store.
            Returns:
                Number of chunks stored
        """
        texts = [c.text for c in chunks]
        ids = [c.chunk_id for c in chunks]
        metadatas = [
            {
                "source_file": c.source_file,
                "chunk_index": c.chunk_index,
                "total_chunk": c.total_chunks
            }
            for c in chunks
        ]

        embeddings = self._embedder.embed_text(texts)

        self._collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )

        logger.info(f"chunks stored", num_chunks=len(chunks))
        return len(chunks)
    
    def search(self, query: str, top_k: Optional[int] = None) -> list[SearchResult]:
        """Perform Similarity search for a query string
        
        Args:
            query (str): The search query string.
            top_k (int, optional): Number of top results to return(defaults to config).
        
        Returns:
            List of SearchResult objects ordered by similarity.
        """

        top_k = top_k or settings.vector_search_top_k
        query_embedding = self._embedder.embed_query(query)

        results = self._collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            search_results.append(
                SearchResult(
                    chunk_id=results["ids"][0][i],
                    text=doc,
                    source_file=meta["source_file"],
                    score = round(1 - dist, 4), # cosine similarity
                    chunk_index = meta.get("chunk_index",0)
                )
            )
        
        logger.info(f"sim_search completed", query=query, query_length = len(query), results_returned=len(search_results))
        return search_results

    def delete_collection(self) -> None:
        """Drop the entire collection (use with caution)."""
        self._client.delete_collection(name=settings.chroma_collection)
        logger.info("collection deleted", collection=settings.chroma_collection)

    @property
    def count(self) -> int:
        """Return the number of vectors currently stored."""
        return self._collection.count()



