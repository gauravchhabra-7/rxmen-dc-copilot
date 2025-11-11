"""
Claude API Service.

Handles interaction with Anthropic's Claude API for diagnosis generation.
"""

from typing import Dict, Any, Optional
import json
import logging
from anthropic import Anthropic
from app.config import settings
from app.models.responses import AnalysisResponse, RootCause, RecommendedAction
from app.services.prompt_service import prompt_service

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Service for interacting with Claude API.

    Constructs prompts, calls Claude API, and parses responses.
    """

    def __init__(self):
        """Initialize Claude service."""
        self.api_key = settings.anthropic_api_key
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.temperature = settings.claude_temperature
        self.client = None

        # Initialize Anthropic client
        if self.api_key and not self.api_key.startswith("sk-ant-xxx"):
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"Claude Service initialized (model: {self.model})")
            except Exception as e:
                logger.error(f"Error initializing Claude client: {str(e)}")
                self.client = None
        else:
            logger.warning("Anthropic API key not configured")

    async def analyze_case(
        self,
        form_data: Dict[str, Any],
        medical_context: str
    ) -> AnalysisResponse:
        """
        Analyze patient case using Claude API.

        Args:
            form_data: Patient form data from discovery call
            medical_context: Relevant medical knowledge from RAG

        Returns:
            Structured analysis response
        """
        if not self.client:
            logger.error("Claude client not initialized")
            return self._create_error_response("Claude API not configured")

        try:
            logger.info("Analyzing case with Claude API...")

            # Load system prompt
            system_prompt = prompt_service.load_system_prompt()

            # Build user prompt
            user_prompt = self._build_user_prompt(form_data, medical_context)

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )

            # Parse response
            response_text = response.content[0].text
            logger.info(f"Received Claude response ({len(response_text)} chars)")

            # Parse JSON response
            analysis_result = self._parse_claude_response(response_text, form_data)

            return analysis_result

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Claude JSON response: {str(e)}")
            return self._create_error_response("Failed to parse AI response")

        except Exception as e:
            logger.error(f"Error in Claude API call: {str(e)}")
            return self._create_error_response(f"AI analysis failed: {str(e)}")

    def _build_user_prompt(
        self,
        form_data: Dict[str, Any],
        medical_context: str
    ) -> str:
        """
        Build user prompt containing form data and context.

        Args:
            form_data: Patient form data
            medical_context: Retrieved medical knowledge

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "Please analyze the following patient case and provide a structured root cause diagnosis:",
            "",
            "## PATIENT FORM DATA",
            "",
            self._format_form_data(form_data),
            "",
            medical_context,
            "",
            "## INSTRUCTIONS",
            "",
            "1. Check for red flags FIRST (refer to red flags checklist)",
            "2. If red flag detected, return red flag response and STOP",
            "3. If no red flags:",
            "   - Identify exactly 2 root causes (1 Physiological + 1 Psychological)",
            "   - Provide simple Hinglish explanations using analogies",
            "   - Link treatment recommendations to identified root causes",
            "   - Use patterns from the treatment explanations document",
            "4. Return response as JSON following the specified format",
            "",
            "Analyze now:"
        ]

        return "\n".join(prompt_parts)

    def _format_form_data(self, form_data: Dict[str, Any]) -> str:
        """Format form data for prompt."""
        sections = []

        # Demographics
        sections.append("### Demographics")
        sections.append(f"- Age: {form_data.get('age')} years")
        sections.append(f"- Weight: {form_data.get('weight')} kg")
        if form_data.get('height_cm'):
            sections.append(f"- Height: {form_data.get('height_cm')} cm")

        # Main Concern
        sections.append("")
        sections.append("### Main Concern")
        sections.append(f"- Primary Issue: {form_data.get('main_issue', 'unknown').upper()}")
        sections.append(f"- Emergency Red Flags: {form_data.get('emergency_red_flags', 'none')}")

        # Medical History
        sections.append("")
        sections.append("### Medical History")
        medical_conditions = form_data.get('medical_conditions', [])
        sections.append(f"- Medical Conditions: {', '.join(medical_conditions) if medical_conditions else 'None reported'}")

        current_meds = form_data.get('current_medications', [])
        sections.append(f"- Current Medications: {', '.join(current_meds) if current_meds else 'None reported'}")

        sections.append(f"- Surgery/Injury History: {form_data.get('spinal_genital_surgery', 'unknown')}")

        # Lifestyle
        sections.append("")
        sections.append("### Lifestyle Factors")
        sections.append(f"- Alcohol: {form_data.get('alcohol_consumption', 'unknown')}")
        sections.append(f"- Smoking: {form_data.get('smoking_status', 'unknown')}")
        sections.append(f"- Sleep Quality: {form_data.get('sleep_quality', 'unknown')}")
        sections.append(f"- Physical Activity: {form_data.get('physical_activity', 'unknown')}")

        # Behavioral Patterns
        sections.append("")
        sections.append("### Behavioral Patterns")
        sections.append(f"- Relationship Status: {form_data.get('relationship_status', 'unknown')}")
        sections.append(f"- Masturbation Method: {form_data.get('masturbation_method', 'unknown')}")
        sections.append(f"- Masturbation Grip: {form_data.get('masturbation_grip', 'unknown')}")
        sections.append(f"- Masturbation Frequency: {form_data.get('masturbation_frequency', 'unknown')}")
        sections.append(f"- Porn Usage Frequency: {form_data.get('porn_frequency', 'unknown')}")

        # ED Specific (if applicable)
        if form_data.get('main_issue') in ['ed', 'both']:
            sections.append("")
            sections.append("### ED-Specific Symptoms")
            sections.append(f"- Gets Erections: {form_data.get('ed_gets_erections', 'unknown')}")
            sections.append(f"- Morning Erections: {form_data.get('ed_morning_erections', 'unknown')}")
            sections.append(f"- Masturbation/Imagination: {form_data.get('ed_masturbation_imagination', 'unknown')}")
            sections.append(f"- Partner Arousal Speed: {form_data.get('ed_partner_arousal_speed', 'unknown')}")
            sections.append(f"- Partner Maintenance: {form_data.get('ed_partner_maintenance', 'unknown')}")
            sections.append(f"- Partner Hardness: {form_data.get('ed_partner_hardness', 'unknown')}")

        # PE Specific (if applicable)
        if form_data.get('main_issue') in ['pe', 'both']:
            sections.append("")
            sections.append("### PE-Specific Symptoms")
            sections.append(f"- Time to Ejaculation: {form_data.get('pe_partner_time_to_ejaculation', 'unknown')}")
            sections.append(f"- Control: {form_data.get('pe_partner_control', 'unknown')}")
            sections.append(f"- Partner Satisfaction: {form_data.get('pe_partner_satisfaction', 'unknown')}")
            sections.append(f"- Masturbation Control: {form_data.get('pe_partner_masturbation_control', 'unknown')}")

        return "\n".join(sections)

    def _parse_claude_response(self, response_text: str, form_data: Dict[str, Any]) -> AnalysisResponse:
        """
        Parse Claude's JSON response into AnalysisResponse model.

        Args:
            response_text: Raw response from Claude
            form_data: Original form data (for fallback)

        Returns:
            AnalysisResponse object
        """
        try:
            # Extract JSON from response (it might be wrapped in markdown code blocks)
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()

            # Parse JSON
            data = json.loads(json_text)

            # Check for red flag
            if data.get("red_flag_detected"):
                red_flag_details = data.get("red_flag_details", {})
                return AnalysisResponse(
                    success=True,
                    primary_diagnosis=f"RED FLAG: {red_flag_details.get('condition', 'Unknown condition')}",
                    root_causes=[],
                    summary=red_flag_details.get('action_required', 'Immediate medical attention required'),
                    recommended_actions=[
                        RecommendedAction(
                            action_type="emergency",
                            description=red_flag_details.get('action_required', 'Escalate immediately'),
                            priority="urgent"
                        )
                    ],
                    red_flags=[red_flag_details.get('condition', 'Unknown')],
                    requires_specialist=True,
                    model_used=self.model,
                    sources_used=[]
                )

            # Parse normal diagnosis
            primary_cause = data.get("primary_root_cause", {})
            secondary_cause = data.get("secondary_root_cause", {})

            root_causes = []

            if primary_cause:
                root_causes.append(RootCause(
                    category=primary_cause.get("medical_term", "Unknown"),
                    confidence="high" if primary_cause.get("confidence", 0) > 0.75 else "medium",
                    explanation=primary_cause.get("simple_explanation", ""),
                    contributing_factors=primary_cause.get("supporting_symptoms", []),
                    analogy=primary_cause.get("simple_explanation", "")[:200]
                ))

            if secondary_cause:
                root_causes.append(RootCause(
                    category=secondary_cause.get("medical_term", "Unknown"),
                    confidence="medium" if secondary_cause.get("confidence", 0) > 0.60 else "low",
                    explanation=secondary_cause.get("simple_explanation", ""),
                    contributing_factors=secondary_cause.get("supporting_symptoms", []),
                    analogy=secondary_cause.get("simple_explanation", "")[:200]
                ))

            # Treatment recommendations
            treatment = data.get("treatment_recommendation", {})
            actions = []

            if treatment:
                if treatment.get("lifestyle_modifications"):
                    actions.append(RecommendedAction(
                        action_type="lifestyle",
                        description=", ".join(treatment.get("lifestyle_modifications", [])),
                        priority="high"
                    ))

                if treatment.get("behavioral_therapy"):
                    actions.append(RecommendedAction(
                        action_type="therapy",
                        description=", ".join(treatment.get("behavioral_therapy", [])),
                        priority="high"
                    ))

                if treatment.get("medical_intervention"):
                    actions.append(RecommendedAction(
                        action_type="medical",
                        description=", ".join(treatment.get("medical_intervention", [])),
                        priority="medium"
                    ))

            # Extract sources from RAG
            sources = []
            if primary_cause.get("rag_sources"):
                sources.extend(primary_cause.get("rag_sources", []))
            if secondary_cause.get("rag_sources"):
                sources.extend(secondary_cause.get("rag_sources", []))

            return AnalysisResponse(
                success=True,
                primary_diagnosis=primary_cause.get("medical_term", "Unknown"),
                root_causes=root_causes,
                summary=treatment.get("summary", ""),
                recommended_actions=actions,
                red_flags=[],
                requires_specialist=False,
                model_used=self.model,
                sources_used=list(set(sources)),
                detailed_analysis=treatment.get("explanation_for_patient", ""),
                conversation_starters=None
            )

        except Exception as e:
            logger.error(f"Error parsing Claude response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            return self._create_error_response(f"Failed to parse response: {str(e)}")

    def _create_error_response(self, error_message: str) -> AnalysisResponse:
        """Create an error response."""
        return AnalysisResponse(
            success=False,
            primary_diagnosis="Analysis Error",
            root_causes=[],
            summary=error_message,
            recommended_actions=[
                RecommendedAction(
                    action_type="system",
                    description="Please try again or contact support",
                    priority="high"
                )
            ],
            red_flags=[],
            requires_specialist=False,
            model_used=self.model,
            sources_used=[]
        )


# Global instance
claude_service = ClaudeService()
