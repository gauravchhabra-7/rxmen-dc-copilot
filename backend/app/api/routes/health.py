"""
Health check endpoint.

Provides system health status and service availability.
"""

from fastapi import APIRouter
from app.models.responses import HealthCheckResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns current system status and external service availability.

    Returns:
        HealthCheckResponse with status information
    """

    logger.info("Health check requested")

    # Check external service status (placeholder)
    services_status = {
        "claude_api": settings.anthropic_api_key is not None,
        "openai_api": settings.openai_api_key is not None,
        "pinecone": settings.pinecone_api_key is not None,
    }

    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        services=services_status
    )


@router.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - redirects to health check.

    Returns:
        Basic API information
    """
    return {
        "message": "RxMen Discovery Call Copilot API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }
