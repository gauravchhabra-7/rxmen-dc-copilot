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
from app.utils.qa_context_builder import (
    build_qa_context,
    format_qa_context_for_prompt,
    get_diagnostic_highlights
)

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
            logger.info("="*80)
            logger.info("ANALYZING CASE WITH PERSONALIZATION")
            logger.info("="*80)

            # Load system prompt
            system_prompt = prompt_service.load_system_prompt()
            logger.info(f"System prompt loaded ({len(system_prompt)} chars)")

            # Build user prompt with Q&A context
            user_prompt = self._build_user_prompt(form_data, medical_context)
            logger.info(f"User prompt built ({len(user_prompt)} chars)")

            # Log first 500 chars of Q&A context for debugging
            if "PATIENT QUESTION-ANSWER CONTEXT" in user_prompt:
                qa_section = user_prompt.split("PATIENT QUESTION-ANSWER CONTEXT")[1][:500]
                logger.info(f"Q&A Context Preview: {qa_section}...")

            # Call Claude API
            logger.info("Calling Claude API...")
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
            logger.info(f"✓ Received Claude response ({len(response_text)} chars)")

            # Log response preview
            preview = response_text[:300] if len(response_text) > 300 else response_text
            logger.info(f"Response preview: {preview}...")

            # Parse JSON response
            analysis_result = self._parse_claude_response(response_text, form_data)

            # Log personalization check
            primary_explanation = analysis_result.root_causes[0].explanation if analysis_result.root_causes else ""
            if "aapne bataya" in primary_explanation.lower() or "aapne mention" in primary_explanation.lower():
                logger.info("✓ PERSONALIZATION DETECTED: Response references patient's answers")
            else:
                logger.warning("⚠ PERSONALIZATION WARNING: Response may not reference patient's specific answers")

            logger.info("="*80)

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
        Build user prompt with Q&A context for personalized responses.

        Args:
            form_data: Patient form data
            medical_context: Retrieved medical knowledge

        Returns:
            Formatted prompt string with Q&A context
        """
        # Build Q&A context
        qa_pairs = build_qa_context(form_data)
        qa_context = format_qa_context_for_prompt(qa_pairs)

        # Get diagnostic highlights
        main_issue = form_data.get('main_issue', 'unknown')
        diagnostic_highlights = get_diagnostic_highlights(qa_pairs, main_issue)

        # Log Q&A context for debugging
        logger.info(f"Built Q&A context with {len(qa_pairs)} question-answer pairs")

        prompt_parts = [
            "Please analyze this patient case and provide a PERSONALIZED root cause diagnosis.",
            "",
            "CRITICAL: You MUST reference the patient's specific answers in your explanation.",
            "Use phrases like 'Aapne bataya ki...' to show you understood their situation.",
            "",
            "---",
            "",
            qa_context,
            "",
            "---",
            "",
            diagnostic_highlights if diagnostic_highlights else "",
            "",
            "---",
            "",
            medical_context,
            "",
            "---",
            "",
            "## INSTRUCTIONS FOR THIS CASE",
            "",
            "1. **Red Flag Check**: Scan Q&A context for emergency conditions FIRST",
            "2. **If red flag detected**: Return red flag response immediately and STOP",
            "3. **If no red flags**:",
            "   - Identify exactly 2 root causes (1 Physiological + 1 Psychological)",
            "   - In your explanation, REFERENCE specific patient answers (e.g., 'Aapne bataya ki...')",
            "   - Build logical reasoning: \"You said X → This indicates Y → Therefore Z\"",
            "   - Use simple Hinglish with analogies from training",
            "   - Link treatment to THEIR specific symptoms (not generic therapy)",
            "4. **Return JSON** following the exact format specified in system prompt",
            "",
            "**Remember**: Personalization is NON-NEGOTIABLE. Every explanation must feel like it's specifically for THIS patient.",
            "",
            "Analyze now:"
        ]

        return "\n".join(prompt_parts)

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
                    simple_term=primary_cause.get("simple_term"),
                    confidence="high" if primary_cause.get("confidence", 0) > 0.75 else "medium",
                    explanation=primary_cause.get("simple_explanation", ""),
                    contributing_factors=primary_cause.get("supporting_symptoms", []),
                    analogy=primary_cause.get("simple_explanation", "")[:200]
                ))

            if secondary_cause:
                root_causes.append(RootCause(
                    category=secondary_cause.get("medical_term", "Unknown"),
                    simple_term=secondary_cause.get("simple_term"),
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
