"""
Embedding service for generating vector embeddings
"""
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings as ChromaSettings
import chromadb
from ..config import settings


class EmbeddingService:
    """Service for managing embeddings and vector store"""

    def __init__(self):
        """Initialize embedding service"""
        self.embeddings = None
        self.vectorstore = None
        self._initialize()

    def _initialize(self):
        """Initialize embeddings and vector store"""
        # Initialize OpenAI embeddings
        if settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )

            # Initialize Chroma vector store
            chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )

            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="notes",
                embedding_function=self.embeddings,
            )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add texts to vector store

        Args:
            texts: List of text chunks
            metadatas: List of metadata dicts
            ids: List of IDs

        Returns:
            List of vector IDs
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Please set OPENAI_API_KEY.")

        vector_ids = self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        return vector_ids

    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter: dict = None
    ) -> List[tuple]:
        """
        Search for similar texts

        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter

        Returns:
            List of (Document, score) tuples
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Please set OPENAI_API_KEY.")

        k = k or settings.TOP_K

        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )
        return results

    def delete_by_ids(self, ids: List[str]) -> bool:
        """
        Delete vectors by IDs

        Args:
            ids: List of vector IDs

        Returns:
            True if deleted successfully
        """
        if not self.vectorstore:
            return False

        try:
            self.vectorstore.delete(ids=ids)
            return True
        except Exception:
            return False

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        if not self.embeddings:
            raise ValueError("Embeddings not initialized. Please set OPENAI_API_KEY.")

        return self.embeddings.embed_query(query)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents

        Args:
            documents: List of document texts

        Returns:
            List of embedding vectors
        """
        if not self.embeddings:
            raise ValueError("Embeddings not initialized. Please set OPENAI_API_KEY.")

        return self.embeddings.embed_documents(documents)


# Global instance
embedding_service = EmbeddingService()
