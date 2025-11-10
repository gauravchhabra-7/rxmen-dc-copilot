"""
Analysis endpoint.

Handles patient form data submission and returns AI-generated diagnosis.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.requests import FormDataRequest
from app.models.responses import AnalysisResponse, ErrorResponse
from app.services.rag_service import rag_service
from app.services.claude_service import claude_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid form data"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    tags=["Analysis"]
)
async def analyze_patient_case(form_data: FormDataRequest):
    """
    Analyze patient case and return root cause diagnosis.

    This endpoint:
    1. Receives form data from the discovery call
    2. Retrieves relevant medical knowledge using RAG
    3. Sends data + context to Claude API
    4. Returns structured diagnosis with root causes

    Args:
        form_data: Complete patient form data from frontend

    Returns:
        AnalysisResponse with root causes, explanations, and recommendations

    Raises:
        HTTPException: If analysis fails or form data is invalid
    """

    try:
        logger.info(f"Received analysis request for patient age {form_data.age}, issue: {form_data.main_issue}")

        # Step 1: Check for emergency red flags
        if form_data.emergency_red_flags and form_data.emergency_red_flags != "none":
            logger.warning(f"Emergency red flag detected: {form_data.emergency_red_flags}")
            # Red flags are handled by frontend, but we log for audit
            pass

        # Step 2: Retrieve relevant medical knowledge using RAG
        logger.info("Retrieving relevant medical context...")
        medical_context = await rag_service.retrieve_context_for_diagnosis(
            form_data.model_dump()
        )

        # Step 3: Analyze using Claude API
        logger.info("Analyzing case with Claude API...")
        analysis = await claude_service.analyze_case(
            form_data=form_data.model_dump(),
            medical_context=medical_context
        )

        logger.info(f"Analysis completed successfully: {analysis.primary_diagnosis}")
        return analysis

    except ValueError as e:
        logger.error(f"Validation error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "ValidationError",
                "message": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
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
    return {
        "message": "Analyze endpoint is working",
        "status": "ready",
        "note": "Send POST request with FormDataRequest to /analyze for actual analysis"
    }
