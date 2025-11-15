"""
Response models for API endpoints.

Defines Pydantic schemas for outgoing API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RootCause(BaseModel):
    """
    Individual root cause identified by the AI.
    """
    category: str = Field(..., description="Root cause category (e.g., 'Performance Anxiety', 'Venous Leak')")
    simple_term: Optional[str] = Field(None, description="2-4 word simple label in plain language (e.g., 'Performance anxiety', 'Weak pelvic muscles')")
    confidence: str = Field(..., description="Confidence level: high, medium, low")
    explanation: str = Field(..., description="Patient-friendly explanation of this root cause")
    contributing_factors: List[str] = Field(default_factory=list, description="Specific factors from form data")
    analogy: Optional[str] = Field(None, description="Analogy to help patient understand")


class RecommendedAction(BaseModel):
    """
    Recommended next steps or actions.
    """
    action_type: str = Field(..., description="Type: consultation, lifestyle, treatment, etc.")
    description: str = Field(..., description="Description of recommended action")
    priority: str = Field(..., description="Priority: urgent, high, medium, low")


class AnalysisResponse(BaseModel):
    """
    Response model for the /analyze endpoint.

    Contains AI-generated root cause analysis and recommendations.
    """
    success: bool = Field(..., description="Whether analysis was successful")

    # Primary Results
    primary_diagnosis: str = Field(..., description="Primary diagnosis category")
    root_causes: List[RootCause] = Field(default_factory=list, description="Identified root causes")
    summary: str = Field(..., description="Overall summary for the agent")

    # Recommendations
    recommended_actions: List[RecommendedAction] = Field(
        default_factory=list,
        description="Recommended next steps"
    )

    # Red Flags
    red_flags: List[str] = Field(default_factory=list, description="Any red flags identified")
    requires_specialist: bool = Field(default=False, description="Whether specialist referral needed")

    # Metadata
    analysis_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When analysis was performed"
    )
    model_used: str = Field(..., description="Claude model version used")
    sources_used: List[str] = Field(default_factory=list, description="Medical knowledge sources referenced")

    # Optional detailed output
    detailed_analysis: Optional[str] = Field(None, description="Full detailed analysis text")
    conversation_starters: Optional[List[str]] = Field(None, description="Suggested conversation starters for agent")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": True,
                "primary_diagnosis": "Performance Anxiety with Situational ED",
                "root_causes": [
                    {
                        "category": "Performance Anxiety",
                        "confidence": "high",
                        "explanation": "Fear of not performing well during sex creates a self-fulfilling cycle",
                        "contributing_factors": ["Avoids sex due to worry", "Works fine during masturbation"],
                        "analogy": "Like stage fright - the more you worry about forgetting lines, the more likely it happens"
                    }
                ],
                "summary": "Patient shows classic signs of performance anxiety...",
                "recommended_actions": [
                    {
                        "action_type": "treatment",
                        "description": "Consider PDE5 inhibitors to break anxiety cycle",
                        "priority": "high"
                    }
                ],
                "red_flags": [],
                "requires_specialist": False,
                "model_used": "claude-3-5-sonnet-20241022",
                "sources_used": ["ED_training_Module", "Analogies_with_Root_Causes"]
            }
        }


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint.
    """
    status: str = Field(..., description="Health status")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Current server timestamp"
    )
    version: str = Field(..., description="API version")
    services: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of external services"
    )


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="When error occurred"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid form data provided",
                "details": {"field": "age", "issue": "Age must be between 18 and 120"},
                "timestamp": "2025-01-10T17:00:00Z"
            }
        }
