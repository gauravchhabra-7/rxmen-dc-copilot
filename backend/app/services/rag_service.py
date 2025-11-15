"""
RAG (Retrieval-Augmented Generation) Service.

Handles retrieval of relevant medical knowledge from Pinecone vector database.
"""

from typing import List, Dict, Any
import logging
from pinecone import Pinecone
from openai import OpenAI
from app.config import settings
from app.utils.form_to_query import form_data_to_query

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for retrieving relevant medical knowledge using RAG.

    Uses Pinecone vector database and OpenAI embeddings to find
    relevant chunks from medical training documents.
    """

    def __init__(self):
        """Initialize RAG service with vector database connection."""
        self.initialized = False
        self.pinecone_client = None
        self.index = None
        self.openai_client = None
        self.namespace = "medical_knowledge_v1"

        try:
            # Initialize Pinecone
            if settings.pinecone_api_key and not settings.pinecone_api_key.startswith("xxx"):
                self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
                self.index = self.pinecone_client.Index(settings.pinecone_index_name)
                logger.info(f"Pinecone initialized (index: {settings.pinecone_index_name})")
            else:
                logger.warning("Pinecone API key not configured")

            # Initialize OpenAI for embeddings
            if settings.openai_api_key and not settings.openai_api_key.startswith("sk-xxx"):
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI client initialized for embeddings")
            else:
                logger.warning("OpenAI API key not configured")

            self.initialized = self.pinecone_client is not None and self.openai_client is not None

            if self.initialized:
                logger.info("RAG Service fully initialized")
            else:
                logger.warning("RAG Service initialized with limitations (missing API keys)")

        except Exception as e:
            logger.error(f"Error initializing RAG Service: {str(e)}")
            self.initialized = False

    async def retrieve_relevant_context(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant medical knowledge for a query.

        Args:
            query: The search query (e.g., patient symptoms, diagnosis)
            top_k: Number of relevant chunks to retrieve (defaults to RAG_TOP_K setting)

        Returns:
            List of relevant knowledge chunks with metadata
        """
        if not self.initialized:
            logger.error("RAG Service not initialized")
            return []

        if top_k is None:
            top_k = settings.rag_top_k

        try:
            logger.info(f"Retrieving context for query: {query[:100]}... (top_k={top_k})")

            # Generate query embedding
            embedding_response = self.openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=query
            )
            query_embedding = embedding_response.data[0].embedding

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.namespace,
                include_metadata=True
            )

            # Format results
            chunks = []
            for match in results.matches:
                chunk = {
                    "chunk_id": match.id,
                    "text": match.metadata.get("text", ""),
                    "source_file": match.metadata.get("source_file", "unknown"),
                    "root_cause": match.metadata.get("root_cause", "unknown"),
                    "document_type": match.metadata.get("document_type", "unknown"),
                    "relevance_score": float(match.score)
                }
                chunks.append(chunk)

            logger.info(f"Retrieved {len(chunks)} chunks (top score: {chunks[0]['relevance_score']:.4f})")

            return chunks

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []

    async def retrieve_context_for_diagnosis(
        self,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retrieve relevant medical knowledge based on form data.

        Args:
            form_data: Patient form data dictionary

        Returns:
            Dictionary containing formatted context and retrieved chunks
        """
        try:
            logger.info("Retrieving diagnostic context from form data")

            # Convert form data to search query
            query = form_data_to_query(form_data)

            # Retrieve relevant chunks
            chunks = await self.retrieve_relevant_context(query)

            # Format context for Claude
            formatted_context = self._format_context_for_claude(chunks)

            return {
                "formatted_context": formatted_context,
                "chunks": chunks,
                "query_used": query,
                "chunks_retrieved": len(chunks)
            }

        except Exception as e:
            logger.error(f"Error in retrieve_context_for_diagnosis: {str(e)}")
            return {
                "formatted_context": "Error retrieving medical context.",
                "chunks": [],
                "query_used": "",
                "chunks_retrieved": 0
            }

    def _format_context_for_claude(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context string for Claude.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant medical knowledge found in the database."

        context_parts = [
            "## RETRIEVED MEDICAL KNOWLEDGE",
            "",
            f"Retrieved {len(chunks)} relevant medical knowledge chunks:",
            ""
        ]

        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"### Source {i}: {chunk['chunk_id']}")
            context_parts.append(f"**Root Cause Category:** {chunk['root_cause']}")
            context_parts.append(f"**Document:** {chunk['source_file']}")
            context_parts.append(f"**Relevance Score:** {chunk['relevance_score']:.4f}")
            context_parts.append("")
            context_parts.append(f"**Content:**")
            context_parts.append(chunk['text'][:1000])  # Limit to first 1000 chars
            context_parts.append("")
            context_parts.append("---")
            context_parts.append("")

        return "\n".join(context_parts)


# Global instance
rag_service = RAGService()
