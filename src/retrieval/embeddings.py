###Embeddings generation using Vertex AI text-embedding-004.

# =============================================================================
# Test: make seed -> ChromeDB vector store populated at data/embeddings/
# =============================================================================

import structlog
from langchain_google_vertexai import VertexAIEmbeddings
from app.core.config import settings

logger = structlog.get_logger()

class EmbeddingClient:
    """Vertex AI embedding client wrapper """

    def __init__(self) -> None:
        self.model_name = settings.embedding_model
        self._client = VertexAIEmbeddings(
            model=self.model_name,
            project=settings.gcp_project_id,
            location=settings.gcp_location,)
        logger.info(f"Initialized VertexAIEmbeddings client with model {self.model_name}")

    def embed_text(self, texts : list[str]) -> list[list[float]]:
        """Geberate enbeddings for a list of texts strings.

        Args:
            texts (list[str]): List of text strings to embed.

        Returns:
            List of float vectors, one per input text.
        """
        logger.debug("embedding texts", count=len(texts))
        vectors = self._client.embed_documents(texts)
        logger.debug("generated embeddings", count=len(vectors), dims=len(vectors[0]) if vectors else 0)
        return vectors
    
    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single search query.

        Args:
            query (str): The search query to embed.

        Returns:
            List of float values representing the query.
        """
        logger.debug("embedding query", query=query)
        vector = self._client.embed_query(query)
        logger.debug("generated query embedding", dims=len(vector) if vector else 0)
        return vector