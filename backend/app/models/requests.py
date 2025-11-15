"""
Request models for API endpoints.

Defines Pydantic schemas for incoming API requests with validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class FormDataRequest(BaseModel):
    """
    Request model for the /analyze endpoint.

    Contains all form data collected from the RxMen Discovery Call form.
    """

    # Section 1: Client Information
    age: int = Field(..., ge=18, le=120, description="Patient age")
    height_cm: Optional[float] = Field(None, description="Height in centimeters")
    height_ft: Optional[int] = Field(None, description="Height in feet")
    height_in: Optional[int] = Field(None, description="Height in inches")
    weight: float = Field(..., gt=0, description="Weight in kg")

    # Section 2: Main Concern
    main_issue: str = Field(..., description="Primary concern: ed, pe, or both")
    emergency_red_flags: str = Field(..., description="Emergency red flag selection")

    # Section 3: Medical & Lifestyle
    medical_conditions: list[str] = Field(default_factory=list, description="Medical conditions")
    current_medications: list[str] = Field(default_factory=list, description="Current medications")
    spinal_genital_surgery: str = Field(..., description="Surgery/injury history")
    alcohol_consumption: str = Field(..., description="Alcohol frequency")
    smoking_status: str = Field(..., description="Smoking status")
    substance_consumption: Optional[str] = Field(None, description="Other substances")
    sleep_quality: str = Field(..., description="Sleep quality")
    physical_activity: str = Field(..., description="Exercise frequency")

    # Section 4: Masturbation & Behavioral History
    relationship_status: str = Field(..., description="Relationship status")
    masturbation_method: str = Field(..., description="Masturbation method")
    masturbation_grip: Optional[str] = Field(None, description="Grip type if applicable")
    masturbation_frequency: Optional[str] = Field(None, description="Masturbation frequency")
    porn_frequency: str = Field(..., description="Pornography usage")
    partner_response: Optional[str] = Field(None, description="Partner response if applicable")

    # Section 5: ED/PE Branch
    # ED Branch (5A)
    ed_gets_erections: Optional[str] = Field(None, description="Gets erections at all")
    ed_sexual_activity_status: Optional[str] = Field(None, description="Sexual activity with partner")
    ed_partner_arousal_speed: Optional[str] = Field(None, description="Time to get erections")
    ed_partner_maintenance: Optional[str] = Field(None, description="Erection maintenance")
    ed_partner_hardness: Optional[str] = Field(None, description="Erection hardness")
    ed_morning_erections: Optional[str] = Field(None, description="Morning erection frequency")
    ed_masturbation_imagination: Optional[str] = Field(None, description="Erections during masturbation/fantasy")

    # PE Branch (5B)
    pe_sexual_activity_status: Optional[str] = Field(None, description="PE sexual activity status")
    pe_partner_time_to_ejaculation: Optional[str] = Field(None, description="Time to ejaculation with partner")
    pe_partner_control: Optional[str] = Field(None, description="Control during partnered sex")
    pe_partner_satisfaction: Optional[str] = Field(None, description="Partner satisfaction")
    pe_partner_masturbation_control: Optional[str] = Field(None, description="Control during masturbation")

    # Section 6: Other Information
    first_consultation: str = Field(..., description="First consultation or follow-up")
    previous_treatments: Optional[list[str]] = Field(None, description="Previous treatments if any")
    additional_info: Optional[str] = Field(None, description="Additional notes")

    # Metadata
    form_version: str = Field(default="2.2", description="Form version")
    submitted_at: Optional[str] = Field(None, description="Submission timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "age": 32,
                "height_cm": 175,
                "weight": 75,
                "main_issue": "ed",
                "emergency_red_flags": "none",
                "medical_conditions": ["none"],
                "current_medications": ["none"],
                "spinal_genital_surgery": "no",
                "alcohol_consumption": "once_week",
                "smoking_status": "never",
                "sleep_quality": "good",
                "physical_activity": "moderate",
                "relationship_status": "married",
                "masturbation_method": "hands",
                "masturbation_grip": "normal",
                "masturbation_frequency": "3_to_7",
                "porn_frequency": "3_to_5",
                "ed_gets_erections": "yes",
                "first_consultation": "yes"
            }
        }


class HealthCheckRequest(BaseModel):
    """
    Optional request model for health check endpoint.

    Can be used to test connectivity with payload.
    """
    ping: Optional[str] = Field(None, description="Ping message")
