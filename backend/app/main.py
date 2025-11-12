"""
RxMen Discovery Call Copilot - FastAPI Backend.

Main application entry point. Configures FastAPI app with routes, middleware,
and dependencies.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.api.routes import health, analyze
from app.utils.logger import setup_logger
import logging

# Set up logging
logger = setup_logger("rxmen-api", level=logging.INFO)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-powered root cause analysis system for ED/PE discovery calls.

    ## Features

    * **Health Check**: System status and service availability
    * **Analysis**: AI-driven diagnosis with root cause identification
    * **RAG Integration**: Retrieves relevant medical knowledge
    * **Claude API**: Uses Claude for intelligent analysis

    ## Workflow

    1. Frontend submits patient form data
    2. Backend retrieves relevant medical knowledge (RAG)
    3. Claude analyzes case with context
    4. Returns structured diagnosis with root causes

    ## Authentication

    MVP version - no authentication required.
    Future versions will integrate with main RxMen backend.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.

    Initializes connections, loads data, performs health checks.
    """
    logger.info("="*80)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("="*80)

    # Check if API keys are configured
    if not settings.anthropic_api_key:
        logger.warning("⚠️  ANTHROPIC_API_KEY not configured - Claude API calls will fail")

    if not settings.openai_api_key:
        logger.warning("⚠️  OPENAI_API_KEY not configured - Embeddings will fail")

    if not settings.pinecone_api_key:
        logger.warning("⚠️  PINECONE_API_KEY not configured - RAG will fail")

    # Log configuration
    logger.info(f"Claude Model: {settings.claude_model}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Medical Knowledge Path: {settings.medical_knowledge_path}")

    logger.info("Application started successfully")
    logger.info("="*80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.

    Cleanup connections, save state, etc.
    """
    logger.info("Shutting down application...")
    # Add cleanup logic here if needed


# Validation error handler (for 422 errors)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors (422) and log details.

    Args:
        request: The request that caused the validation error
        exc: The validation exception with error details

    Returns:
        JSON response with detailed validation errors
    """
    logger.error("❌ Validation Error (422):")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Validation errors: {exc.errors()}")

    # Log each error in detail
    for error in exc.errors():
        logger.error(f"  - Field: {error.get('loc')}, Type: {error.get('type')}, Message: {error.get('msg')}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please contact support if this persists."
        }
    )


# Health check at root
@app.get("/")
async def root():
    """Root endpoint - returns API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
