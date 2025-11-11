"""
System Prompt Service.

Loads and caches system prompt components from markdown files.
"""

from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PromptService:
    """
    Service for loading and managing system prompts.

    Loads the 4 system prompt component documents and combines them
    into the full system prompt for Claude API.
    """

    def __init__(self):
        """Initialize prompt service and load prompts."""
        self.prompts_loaded = False
        self._system_prompt = None
        self._components = {}

        # Path to system prompt components
        self.prompts_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "system_prompt_components"

        logger.info("Prompt Service initialized")

    def load_system_prompt(self) -> str:
        """
        Load complete system prompt from components.

        Returns:
            Complete system prompt string
        """
        if self._system_prompt is not None:
            return self._system_prompt

        logger.info("Loading system prompt components...")

        # Load all 4 component files
        components = {
            "red_flags": self._load_component("red_flags.md"),
            "analogies": self._load_component("analogies.md"),
            "wrong_explanations": self._load_component("wrong_explanations.md"),
            "treatment_explanations": self._load_component("treatment_explanations.md")
        }

        self._components = components

        # Build complete system prompt
        self._system_prompt = self._build_complete_prompt(components)

        self.prompts_loaded = True
        logger.info(f"System prompt loaded ({len(self._system_prompt)} characters)")

        return self._system_prompt

    def _load_component(self, filename: str) -> str:
        """Load a single prompt component file."""
        file_path = self.prompts_dir / filename

        if not file_path.exists():
            logger.error(f"Prompt component not found: {filename}")
            return f"[ERROR: {filename} not found]"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"Loaded {filename} ({len(content)} characters)")
            return content

        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return f"[ERROR loading {filename}]"

    def _build_complete_prompt(self, components: Dict[str, str]) -> str:
        """
        Build complete system prompt from components.

        Args:
            components: Dictionary of loaded component content

        Returns:
            Complete formatted system prompt
        """
        prompt_parts = [
            "# RxMen Discovery Call Copilot - AI Medical Assistant",
            "",
            "## Your Role",
            "",
            "You are a medical AI assistant helping RxMen discovery call agents diagnose sexual health conditions (ED/PE) during patient consultations.",
            "",
            "### Core Responsibilities",
            "",
            "1. **Analyze patient form data** to identify root causes",
            "2. **Provide exactly 2 root causes**: 1 Physiological/Physical + 1 Psychological",
            "3. **Generate simple Hinglish explanations** agents can read to patients",
            "4. **Link treatment recommendations** to identified root causes",
            "5. **Ensure medical accuracy** while maintaining conversational tone",
            "",
            "---",
            "",
            "## CRITICAL: Red Flags Safety Protocol",
            "",
            components.get("red_flags", ""),
            "",
            "---",
            "",
            "## Patient Explanation Style Guide",
            "",
            components.get("analogies", ""),
            "",
            "---",
            "",
            "## Treatment Explanation Framework",
            "",
            components.get("treatment_explanations", ""),
            "",
            "---",
            "",
            "## Anti-Patterns: Phrases to NEVER Use",
            "",
            components.get("wrong_explanations", ""),
            "",
            "---",
            "",
            "## Output Format Requirements",
            "",
            "Return JSON with exactly this structure:",
            "",
            "```json",
            "{",
            '  "red_flag_detected": false,',
            '  "red_flag_details": null,',
            '  "primary_root_cause": {',
            '    "category": "Physiological|Psychological",',
            '    "medical_term": "Exact medical diagnosis",',
            '    "simple_explanation": "Hinglish explanation using analogies (2-3 sentences)",',
            '    "confidence": 0.85,',
            '    "supporting_symptoms": ["Specific form data points"],',
            '    "rag_sources": ["chunk_id_1", "chunk_id_2"]',
            "  },",
            '  "secondary_root_cause": {',
            '    "category": "Physiological|Psychological",',
            '    "medical_term": "Exact medical diagnosis",',
            '    "simple_explanation": "Hinglish explanation using analogies (2-3 sentences)",',
            '    "confidence": 0.75,',
            '    "supporting_symptoms": ["Specific form data points"],',
            '    "rag_sources": ["chunk_id_3"]',
            "  },",
            '  "treatment_recommendation": {',
            '    "summary": "Combined treatment approach",',
            '    "lifestyle_modifications": ["Specific recommendations"],',
            '    "behavioral_therapy": ["Specific techniques"],',
            '    "medical_intervention": ["Specific options with doctor guidance"],',
            '    "explanation_for_patient": "Hinglish treatment explanation"',
            "  }",
            "}",
            "```",
            "",
            "### If Red Flag Detected:",
            "",
            "```json",
            "{",
            '  "red_flag_detected": true,',
            '  "red_flag_details": {',
            '    "condition": "Condition name",',
            '    "action_required": "Specific action",',
            '    "severity": "Emergency|Urgent|High"',
            "  },",
            '  "primary_root_cause": null,',
            '  "secondary_root_cause": null,',
            '  "treatment_recommendation": null',
            "}",
            "```",
            "",
            "## Quality Checklist",
            "",
            "- ✅ Red flag check completed FIRST",
            "- ✅ Exactly 2 root causes (1 physical + 1 psychological)",
            "- ✅ Confidence scores between 0.0-1.0",
            "- ✅ Explanations use simple Hinglish",
            "- ✅ Analogies are relatable and clear",
            "- ✅ No forbidden phrases used",
            "- ✅ Treatment linked to root causes",
            "- ✅ Hopeful, treatable tone maintained",
            "",
            "---",
            "",
            "**Remember:** Safety first, always check red flags before diagnosis. Base all diagnoses on retrieved medical knowledge. Use Hinglish analogies. Emphasize treatability and hope."
        ]

        return "\n".join(prompt_parts)

    def get_component(self, component_name: str) -> Optional[str]:
        """
        Get a specific component by name.

        Args:
            component_name: Name of component (red_flags, analogies, etc.)

        Returns:
            Component content or None if not found
        """
        if not self.prompts_loaded:
            self.load_system_prompt()

        return self._components.get(component_name)


# Global instance
prompt_service = PromptService()
