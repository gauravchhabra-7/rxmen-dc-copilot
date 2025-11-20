"""
Analysis endpoint.

Handles patient form data submission and returns AI-generated diagnosis.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
import time
from app.models.requests import FormDataRequest
from app.models.responses import AnalysisResponse, ErrorResponse
from app.services.rag_service import rag_service
from app.services.claude_service import claude_service
from app.services.sheets_service import sheets_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid form data"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    tags=["Analysis"]
)
async def analyze_patient_case(form_data: FormDataRequest, background_tasks: BackgroundTasks):
    """
    Analyze patient case and return root cause diagnosis.

    This endpoint:
    1. Receives form data from the discovery call
    2. Retrieves relevant medical knowledge using RAG (Pinecone + OpenAI embeddings)
    3. Loads system prompt (4 documents: red flags, analogies, wrong explanations, treatment)
    4. Sends data + context + system prompt to Claude API
    5. Returns structured diagnosis with 2 root causes + treatment recommendations
    6. Logs submission to Google Sheets (async, doesn't block response)

    Args:
        form_data: Complete patient form data from frontend
        background_tasks: FastAPI background tasks for async logging

    Returns:
        AnalysisResponse with root causes, explanations, and recommendations

    Raises:
        HTTPException: If analysis fails or form data is invalid
    """
    start_time = time.time()

    try:
        logger.info("="*80)
        logger.info(f"NEW ANALYSIS REQUEST")
        logger.info(f"Patient: Age {form_data.age}, Issue: {form_data.main_issue.upper()}")
        logger.info("="*80)

        # Step 1: Check for emergency red flags in form data
        if form_data.emergency_red_flags and form_data.emergency_red_flags != "none":
            logger.warning(f"⚠️ Emergency red flag in form: {form_data.emergency_red_flags}")
            # Note: Red flags will also be checked by Claude using system prompt

        # Step 2: Retrieve relevant medical knowledge using RAG
        logger.info("Step 1: Retrieving relevant medical context (RAG)...")
        rag_start = time.time()

        rag_result = await rag_service.retrieve_context_for_diagnosis(
            form_data.model_dump()
        )

        rag_time = time.time() - rag_start
        logger.info(f"✓ RAG retrieval completed in {rag_time:.2f}s")
        logger.info(f"  - Query: {rag_result.get('query_used', '')[:100]}...")
        logger.info(f"  - Chunks retrieved: {rag_result.get('chunks_retrieved', 0)}")

        if rag_result.get('chunks'):
            top_chunk = rag_result['chunks'][0]
            logger.info(f"  - Top match: {top_chunk.get('chunk_id')} (score: {top_chunk.get('relevance_score', 0):.4f})")

        # Step 3: Analyze using Claude API with system prompt + RAG context
        logger.info("Step 2: Analyzing with Claude API...")
        claude_start = time.time()

        analysis = await claude_service.analyze_case(
            form_data=form_data.model_dump(),
            medical_context=rag_result.get('formatted_context', '')
        )

        claude_time = time.time() - claude_start
        logger.info(f"✓ Claude analysis completed in {claude_time:.2f}s")

        # Step 4: Log results
        total_time = time.time() - start_time

        logger.info("="*80)
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"Primary Diagnosis: {analysis.primary_diagnosis}")
        logger.info(f"Root Causes Found: {len(analysis.root_causes)}")

        for i, cause in enumerate(analysis.root_causes, 1):
            logger.info(f"  {i}. {cause.category} (confidence: {cause.confidence})")

        logger.info(f"Red Flags: {len(analysis.red_flags)}")
        logger.info(f"Requires Specialist: {analysis.requires_specialist}")

        logger.info(f"\nPerformance:")
        logger.info(f"  - RAG retrieval: {rag_time:.2f}s")
        logger.info(f"  - Claude analysis: {claude_time:.2f}s")
        logger.info(f"  - Total time: {total_time:.2f}s")
        logger.info("="*80)

        # Log to Google Sheets in background (doesn't block response)
        processing_time_ms = total_time * 1000
        background_tasks.add_task(
            sheets_service.log_submission,
            form_data=form_data.model_dump(),
            analysis_result=analysis.model_dump() if analysis else None,
            rag_result=rag_result,
            processing_time_ms=processing_time_ms
        )

        return analysis

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "ValidationError",
                "message": str(e)
            }
        )

    except Exception as e:
        error_message = str(e)

        # Check if it's an API overload error from retry logic
        if "temporarily overloaded" in error_message.lower() or "try submitting" in error_message.lower():
            logger.error(f"❌ API Overload error: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "success": False,
                    "error": "APIOverloadError",
                    "message": error_message,
                    "retry_recommended": True
                }
            )

        # Generic error for all other cases
        logger.error(f"❌ Unexpected error during analysis: {error_message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "ServerError",
                "message": "An unexpected error occurred during analysis. Please try again."
            }
        )


@router.get("/analyze/test", tags=["Analysis"])
async def test_analyze_endpoint():
    """
    Test endpoint to verify analyze route is working.

    Returns:
        Test message confirming endpoint is accessible
    """
    # Check service initialization
    rag_status = "initialized" if rag_service.initialized else "not initialized"
    claude_status = "initialized" if claude_service.client is not None else "not initialized"

    return {
        "message": "Analyze endpoint is operational",
        "status": "ready",
        "services": {
            "rag_service": rag_status,
            "claude_service": claude_status
        },
        "note": "Send POST request with FormDataRequest to /api/v1/analyze for actual analysis"
    }
