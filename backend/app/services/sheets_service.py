"""
Google Sheets logging service.

Logs form submissions and AI analysis results to Google Sheets for tracking and review.
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import os
import json
from app.config import settings

logger = logging.getLogger(__name__)

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SheetsService:
    """
    Service for logging form submissions to Google Sheets.

    Uses gspread library with service account authentication via environment variables.
    """

    def __init__(self):
        """Initialize Google Sheets service."""
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self._initialized = False

    def _initialize(self):
        """
        Initialize Google Sheets connection.

        This is called lazily on first log attempt to avoid blocking app startup.
        """
        if self._initialized:
            return

        try:
            # Load service account credentials from settings (loads from .env file)
            creds_json = settings.google_sheets_credentials
            sheet_id = settings.google_sheet_id

            if not creds_json:
                logger.warning("⚠️ GOOGLE_SHEETS_CREDENTIALS not set - Sheets logging disabled")
                return

            if not sheet_id:
                logger.warning("⚠️ GOOGLE_SHEET_ID not set - Sheets logging disabled")
                return

            # Parse JSON string to dictionary
            creds_dict = json.loads(creds_json)

            # Authenticate with service account
            credentials = Credentials.from_service_account_info(
                creds_dict,
                scopes=SCOPES
            )

            self.client = gspread.authorize(credentials)

            # Open spreadsheet by ID
            self.spreadsheet = self.client.open_by_key(sheet_id)

            # Use first sheet (Testing Log)
            self.worksheet = self.spreadsheet.sheet1

            self._initialized = True
            logger.info("✅ Google Sheets service initialized successfully")

        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in GOOGLE_SHEETS_CREDENTIALS: {str(e)}")
        except FileNotFoundError:
            logger.error(f"❌ Service account credentials invalid")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets: {str(e)}")

    def _initialize_headers(self):
        """Initialize spreadsheet headers (71 columns)."""
        headers = [
            # Session Metadata (3 columns)
            "Session ID",
            "Tester Name",
            "Form Completion Time (seconds)",

            # Submission Metadata (3 columns)
            "Submission Timestamp",
            "Form Version",
            "Backend Processing Time (ms)",

            # Patient Input - Section 1: Client Information (4 columns)
            "Age",
            "Height (cm)",
            "Height (ft-in)",
            "Weight (kg)",

            # Patient Input - Section 2: Main Concern (2 columns)
            "Main Issue",
            "Emergency Red Flags",

            # Patient Input - Section 3: Medical & Lifestyle (8 columns)
            "Medical Conditions",
            "Current Medications",
            "Spinal/Genital Surgery",
            "Alcohol Consumption",
            "Smoking Status",
            "Substance Consumption",
            "Sleep Quality",
            "Physical Activity",

            # Patient Input - Section 4: Masturbation & Behavioral History (6 columns)
            "Relationship Status",
            "Masturbation Method",
            "Masturbation Grip",
            "Masturbation Frequency",
            "Porn Frequency",
            "Partner Response",

            # Patient Input - Section 5: ED Branch (7 columns)
            "ED: Gets Erections",
            "ED: Sexual Activity Status",
            "ED: Partner Arousal Speed",
            "ED: Partner Maintenance",
            "ED: Partner Hardness",
            "ED: Morning Erections",
            "ED: Masturbation/Imagination",

            # Patient Input - Section 5: PE Branch (5 columns)
            "PE: Sexual Activity Status",
            "PE: Time to Ejaculation",
            "PE: Control",
            "PE: Partner Satisfaction",
            "PE: Masturbation Control",

            # Patient Input - Section 6: Other Information (3 columns)
            "First Consultation",
            "Previous Treatments",
            "Additional Info",

            # AI Analysis Output - Root Causes (10 columns)
            "Primary Root Cause (Category)",
            "Primary Root Cause (Simple Term)",
            "Primary Root Cause (Confidence)",
            "Primary Root Cause (Explanation)",
            "Primary Root Cause (Analogy)",
            "Secondary Root Cause (Category)",
            "Secondary Root Cause (Simple Term)",
            "Secondary Root Cause (Confidence)",
            "Secondary Root Cause (Explanation)",
            "Secondary Root Cause (Analogy)",

            # AI Analysis Output - Diagnosis (5 columns)
            "Primary Diagnosis",
            "Detailed Analysis",
            "Summary",
            "Red Flags (Count)",
            "Red Flags (Details)",

            # AI Analysis Output - Treatment (3 columns)
            "Doctor Recommendation",
            "Treatment Confidence",
            "Treatment Notes",

            # RAG Context (3 columns)
            "RAG Chunks Retrieved",
            "RAG Top Match ID",
            "RAG Top Match Score",

            # Doctor Review (3 columns - empty for manual input)
            "Doctor Review Status",
            "Doctor Comments",
            "Doctor Reviewed At"
        ]

        try:
            self.worksheet.update('A1:BS1', [headers])
            logger.info(f"✅ Initialized {len(headers)} column headers")
        except Exception as e:
            logger.error(f"❌ Failed to initialize headers: {str(e)}")

    async def log_submission(
        self,
        form_data: Dict[str, Any],
        analysis_result: Optional[Dict[str, Any]] = None,
        rag_result: Optional[Dict[str, Any]] = None,
        processing_time_ms: Optional[float] = None
    ):
        """
        Log a form submission to Google Sheets.

        This runs asynchronously and won't block the API response.
        Errors are logged but don't crash the application.

        Args:
            form_data: Patient form data from frontend
            analysis_result: AI analysis result (optional)
            rag_result: RAG retrieval result (optional)
            processing_time_ms: Backend processing time in milliseconds
        """
        try:
            # Initialize connection if needed
            self._initialize()

            if not self._initialized or not self.worksheet:
                logger.debug("Sheets logging skipped - not initialized")
                return

            # Prepare row data (71 columns)
            row = self._prepare_row(form_data, analysis_result, rag_result, processing_time_ms)

            # Append row to spreadsheet
            self.worksheet.append_row(row, value_input_option='RAW')

            logger.info(f"✅ Logged submission to Google Sheets - Session ID: {form_data.get('session_id', 'N/A')}")

        except Exception as e:
            # Log error but don't crash
            logger.error(f"❌ Failed to log to Google Sheets: {str(e)}")
            logger.debug(f"Error details: {type(e).__name__}", exc_info=True)

    def _prepare_row(
        self,
        form_data: Dict[str, Any],
        analysis_result: Optional[Dict[str, Any]],
        rag_result: Optional[Dict[str, Any]],
        processing_time_ms: Optional[float]
    ) -> List[Any]:
        """
        Prepare a row of data for Google Sheets (71 columns).

        Returns:
            List of 71 values corresponding to the header columns
        """
        # Helper function to safely get values
        def get(data: Any, key: str, default: Any = "") -> Any:
            if data is None:
                return default
            # Handle dict-like objects
            if isinstance(data, dict):
                value = data.get(key, default)
            # Handle Pydantic models or objects with __dict__
            elif hasattr(data, key):
                value = getattr(data, key, default)
            elif hasattr(data, '__dict__') and key in data.__dict__:
                value = data.__dict__[key]
            else:
                return default

            # Convert lists to comma-separated strings
            if isinstance(value, list):
                # Handle list of dicts/objects
                if value and isinstance(value[0], dict):
                    return ", ".join(str(v) for v in value)
                return ", ".join(str(v) for v in value)
            return value if value is not None else default

        # Extract root causes from analysis (with defensive checks)
        root_causes = []
        if analysis_result and isinstance(analysis_result, dict):
            root_causes = analysis_result.get('root_causes', [])

        # Ensure we have dict objects for root causes
        primary_cause = {}
        secondary_cause = {}
        if len(root_causes) > 0:
            primary_cause = root_causes[0] if isinstance(root_causes[0], dict) else {}
        if len(root_causes) > 1:
            secondary_cause = root_causes[1] if isinstance(root_causes[1], dict) else {}

        # Extract red flags (with defensive checks)
        red_flags = []
        if analysis_result and isinstance(analysis_result, dict):
            red_flags = analysis_result.get('red_flags', [])

        red_flags_count = len(red_flags) if isinstance(red_flags, list) else 0

        # Safely extract red flag details
        red_flags_details = ""
        if red_flags and isinstance(red_flags, list):
            details = []
            for rf in red_flags:
                if isinstance(rf, dict):
                    category = rf.get('category', 'Unknown')
                    action = rf.get('action', 'No action')
                    details.append(f"{category}: {action}")
            red_flags_details = "; ".join(details)

        # Format height (combine ft and inches if available)
        height_ft = get(form_data, 'height_ft')
        height_in = get(form_data, 'height_in')
        height_ft_in = f"{height_ft}'{height_in}\"" if height_ft and height_in else ""

        # Prepare row data (71 columns in order)
        row = [
            # Session Metadata (3)
            get(form_data, 'session_id'),
            get(form_data, 'tester_name'),
            get(form_data, 'completion_time_seconds'),

            # Submission Metadata (3)
            get(form_data, 'submitted_at', datetime.utcnow().isoformat()),
            get(form_data, 'form_version', '2.2'),
            processing_time_ms if processing_time_ms else "",

            # Patient Input - Section 1 (4)
            get(form_data, 'age'),
            get(form_data, 'height_cm'),
            height_ft_in,
            get(form_data, 'weight'),

            # Patient Input - Section 2 (2)
            get(form_data, 'main_issue'),
            get(form_data, 'emergency_red_flags'),

            # Patient Input - Section 3 (8)
            get(form_data, 'medical_conditions'),
            get(form_data, 'current_medications'),
            get(form_data, 'spinal_genital_surgery'),
            get(form_data, 'alcohol_consumption'),
            get(form_data, 'smoking_status'),
            get(form_data, 'substance_consumption'),
            get(form_data, 'sleep_quality'),
            get(form_data, 'physical_activity'),

            # Patient Input - Section 4 (6)
            get(form_data, 'relationship_status'),
            get(form_data, 'masturbation_method'),
            get(form_data, 'masturbation_grip'),
            get(form_data, 'masturbation_frequency'),
            get(form_data, 'porn_frequency'),
            get(form_data, 'partner_response'),

            # Patient Input - Section 5: ED Branch (7)
            get(form_data, 'ed_gets_erections'),
            get(form_data, 'ed_sexual_activity_status'),
            get(form_data, 'ed_partner_arousal_speed'),
            get(form_data, 'ed_partner_maintenance'),
            get(form_data, 'ed_partner_hardness'),
            get(form_data, 'ed_morning_erections'),
            get(form_data, 'ed_masturbation_imagination'),

            # Patient Input - Section 5: PE Branch (5)
            get(form_data, 'pe_sexual_activity_status'),
            get(form_data, 'pe_partner_time_to_ejaculation'),
            get(form_data, 'pe_partner_control'),
            get(form_data, 'pe_partner_satisfaction'),
            get(form_data, 'pe_partner_masturbation_control'),

            # Patient Input - Section 6 (3)
            get(form_data, 'first_consultation'),
            get(form_data, 'previous_treatments'),
            get(form_data, 'additional_info'),

            # AI Analysis Output - Root Causes (10)
            get(primary_cause, 'category'),
            get(primary_cause, 'simple_term'),
            get(primary_cause, 'confidence'),
            get(primary_cause, 'explanation'),
            get(primary_cause, 'analogy'),
            get(secondary_cause, 'category'),
            get(secondary_cause, 'simple_term'),
            get(secondary_cause, 'confidence'),
            get(secondary_cause, 'explanation'),
            get(secondary_cause, 'analogy'),

            # AI Analysis Output - Diagnosis (5)
            get(analysis_result, 'primary_diagnosis') if analysis_result else "",
            get(analysis_result, 'detailed_analysis') if analysis_result else "",
            get(analysis_result, 'summary') if analysis_result else "",
            red_flags_count,
            red_flags_details,

            # AI Analysis Output - Treatment (3)
            get(analysis_result, 'doctor_recommendation') if analysis_result else "",
            get(analysis_result, 'treatment_confidence') if analysis_result else "",
            get(analysis_result, 'treatment_notes') if analysis_result else "",

            # RAG Context (3)
            get(rag_result, 'chunks_retrieved') if rag_result else "",
            self._get_rag_chunk_field(rag_result, 'chunk_id'),
            self._get_rag_chunk_field(rag_result, 'relevance_score'),

            # Doctor Review (3) - empty for manual input
            "",
            "",
            ""
        ]

        return row

    def _get_rag_chunk_field(self, rag_result: Optional[Dict[str, Any]], field_name: str) -> str:
        """
        Safely extract a field from the first RAG chunk.

        Args:
            rag_result: RAG result dictionary
            field_name: Field name to extract from first chunk

        Returns:
            Field value as string, or empty string if not found
        """
        if not rag_result or not isinstance(rag_result, dict):
            return ""

        chunks = rag_result.get('chunks', [])
        if not chunks or not isinstance(chunks, list) or len(chunks) == 0:
            return ""

        first_chunk = chunks[0]
        if not isinstance(first_chunk, dict):
            return ""

        return str(first_chunk.get(field_name, ""))


# Singleton instance
sheets_service = SheetsService()
