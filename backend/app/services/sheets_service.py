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

# Value mapping dictionary - converts backend codes to user-friendly form text
VALUE_MAPPINGS = {
    # Yes/No mappings
    "yes": "Yes",
    "no": "No",
    "true": "Yes",
    "false": "No",

    # Main Issue
    "ed": "Erectile Dysfunction (ED)",
    "pe": "Early Ejaculation (PE)",
    "both": "Both ED and PE",

    # Duration
    "lifelong": "Since my first sexual experience (Lifelong)",
    "less_1_month": "Less than 1 month ago",
    "1_to_6_months": "1-6 months ago",
    "6_to_12_months": "6-12 months ago",
    "1_to_3_years": "1-3 years ago",
    "more_3_years": "More than 3 years ago",

    # Context
    "sex_with_partner": "During sex with partner",
    "masturbation": "During masturbation",
    "both_contexts": "Both (during sex and masturbation)",

    # Occupation
    "corporate": "Corporate Employee",
    "business_owner": "Business Owner / Self-employed",
    "freelancer": "Freelancer",
    "student": "Student",
    "retired": "Retired",
    "unemployed": "Unemployed",

    # Relationship Status
    "married": "Married",
    "in_relationship": "In a relationship",
    "single": "Single",
    "divorced_widowed": "Divorced / Widowed",

    # Alcohol Frequency
    "none": "No alcohol",
    "monthly": "Once a month or less",
    "biweekly": "Once every 2 weeks",
    "weekly": "Once a week",
    "2_3_per_week": "2-3 times per week",
    "daily": "Daily",

    # Smoking Frequency
    "never": "No smoking",
    "occasional": "Occasionally (only while drinking or social events)",
    "few_per_week": "Few times per week",
    "daily_smoking": "Daily",

    # Sleep Quality
    "good": "Good",
    "average": "Average",
    "poor": "Poor",

    # Physical Activity
    "active": "Active",
    "somewhat_active": "Somewhat active",
    "not_active": "Not active",

    # Masturbation Method
    "none": "No masturbation",
    "hands": "Using hands",
    "prone": "Rubbing against surface (prone)",
    "both": "Both hands and rubbing surface",

    # Masturbation Grip
    "normal": "Normal",
    "tight": "Tight",

    # Masturbation Frequency
    "less_than_3": "Less than 3 times per week",
    "3_to_7": "3-7 times per week",
    "8_plus": "8 or more times per week",

    # Porn Frequency
    "less_than_2": "Less than 2 times per week",
    "3_to_5": "3-5 times per week",
    "daily_or_more": "Daily or more",

    # Partner Response
    "supportive": "Supportive",
    "neutral": "Neutral",
    "non_supportive": "Non-supportive",
    "unaware": "Unaware (haven't told them)",

    # ED - Sexual Activity Status
    "yes_active": "Yes, I have sex with a partner",
    "avoiding_due_to_fear": "I have a partner but avoid sex due to worry/fear",
    "no_partner": "No, I don't have a partner",

    # ED - Arousal Speed
    "always": "Always",
    "sometimes": "Sometimes",
    "rarely": "Rarely",

    # ED - Maintenance
    "loses_before_penetration": "Loses hardness before penetration",
    "loses_during_sex": "Stays hard till penetration, then loses it",
    "stays_till_completion": "Stays hard till completion",

    # ED - Hardness
    "always_hard": "Yes, always hard enough",
    "sometimes_hard": "Sometimes hard enough",
    "rarely_hard": "Rarely hard enough",
    "never_hard": "Never hard enough",

    # ED - Morning Erections
    "regular": "Regular (most mornings)",
    "occasional": "Occasional (sometimes)",
    "absent": "Absent (rarely or never)",

    # ED - Masturbation/Imagination
    "both_work": "Yes, during both masturbation and imagination",
    "masturbation_only": "Yes, during masturbation only",
    "imagination_only": "Yes, with imagination/fantasies only",
    "neither": "No, neither works",

    # PE - Ejaculation Time
    "before_penetration": "Before penetration",
    "less_than_1_min": "Less than 1 minute after penetration",
    "1_to_3_min": "1-3 minutes after penetration",
    "more_than_3_min": "More than 3 minutes",

    # PE - Control
    "always_control": "Always can control",
    "sometimes_control": "Sometimes can control",
    "rarely_control": "Rarely can control",

    # Emergency Red Flags
    "severe_pain": "Severe pain in penis/testicles (unbearable, can't touch)",
    "blood": "Blood in urine or semen",
    "priapism": "Erection lasting more than 4 hours (priapism)",
}


def map_value(value, field_name=None):
    """
    Convert backend code to user-friendly text.
    Returns original value if no mapping exists.
    """
    if value is None or value == '':
        return ''

    # Handle lists (multi-select fields)
    if isinstance(value, list):
        if not value:
            return ''
        # Special handling for "none" in lists
        if len(value) == 1 and str(value[0]).lower() == 'none':
            return 'None'
        mapped = [VALUE_MAPPINGS.get(str(v).lower(), str(v)) for v in value]
        return ', '.join(mapped)

    # Convert to string and check mapping
    value_str = str(value).lower()
    return VALUE_MAPPINGS.get(value_str, str(value))


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

        # Debug: Log if missing fields are in form_data
        missing_fields_check = ['full_name', 'city', 'occupation']
        for field in missing_fields_check:
            if field not in form_data or not form_data.get(field):
                logger.warning(f"⚠️ Field '{field}' is missing or empty in form_data")
                # Try alternative key names
                alt_keys = {
                    'full_name': ['name', 'patient_name', 'client_name'],
                    'city': ['location'],
                    'occupation': ['job', 'work']
                }
                if field in alt_keys:
                    for alt_key in alt_keys[field]:
                        if alt_key in form_data and form_data.get(alt_key):
                            logger.info(f"✓ Found alternative key '{alt_key}' for '{field}'")

        # Determine conditional N/A logic
        main_issue = str(get(form_data, 'main_issue', '')).lower()
        has_ed = main_issue in ['ed', 'both']
        has_pe = main_issue in ['pe', 'both']

        relationship_status = str(get(form_data, 'relationship_status', '')).lower()
        has_partner = relationship_status in ['married', 'in_relationship']

        ed_sexual_activity = str(get(form_data, 'ed_sexual_activity_status', '')).lower()
        ed_has_partner_data = ed_sexual_activity in ['yes_active', 'avoiding_due_to_fear']

        pe_sexual_activity = str(get(form_data, 'pe_sexual_activity_status', '')).lower()
        pe_has_partner_data = pe_sexual_activity in ['yes_active', 'avoiding_due_to_fear']

        # Helper function to get value with mapping or N/A
        def get_mapped_or_na(key, condition=True):
            """Get field value, apply mapping, or return N/A if condition not met."""
            if not condition:
                return 'N/A'
            value = get(form_data, key, '')
            return map_value(value) if value != '' else ''

        # Prepare row data (71 columns in EXACT order matching Google Sheet)
        row = [
            # ============================================================
            # SECTION A: Session Metadata (Columns 1-4)
            # ============================================================
            get(form_data, 'session_id'),                                           # 1. Session ID
            get(form_data, 'submitted_at', datetime.utcnow().isoformat()),         # 2. Timestamp
            get(form_data, 'tester_name'),                                         # 3. Tester/Agent Name
            get(form_data, 'completion_time_seconds'),                             # 4. Form Completion Time (sec)

            # ============================================================
            # SECTION B: Patient Input Data (Columns 5-51)
            # ============================================================
            get(form_data, 'full_name'),                                           # 5. Full Name (no mapping needed)
            map_value(get(form_data, 'age')),                                      # 6. Age
            map_value(get(form_data, 'height_cm')),                                # 7. Height (cm)
            map_value(get(form_data, 'weight')),                                   # 8. Weight (kg)
            get(form_data, 'city'),                                                # 9. City (no mapping needed)
            map_value(get(form_data, 'occupation')),                               # 10. Occupation
            map_value(get(form_data, 'relationship_status')),                      # 11. Relationship Status
            map_value(get(form_data, 'first_consultation')),                       # 12. First Consultation
            map_value(get(form_data, 'previous_treatments')),                      # 13. Previous Treatments
            map_value(get(form_data, 'emergency_red_flags')),                      # 14. Emergency Red Flags
            map_value(get(form_data, 'main_issue')),                               # 15. Main Issue
            map_value(get(form_data, 'issue_duration')),                           # 16. Issue Duration
            map_value(get(form_data, 'issue_context')),                            # 17. Issue Context
            map_value(get(form_data, 'medical_conditions')),                       # 18. Medical Conditions
            get(form_data, 'medical_conditions_other'),                            # 19. Medical Conditions - Other
            map_value(get(form_data, 'current_medications')),                      # 20. Current Medications
            get(form_data, 'current_medications_other'),                           # 21. Current Medications - Other
            map_value(get(form_data, 'spinal_genital_surgery')),                   # 22. Spinal/Genital Surgery
            map_value(get(form_data, 'alcohol_consumption')),                      # 23. Alcohol Frequency
            map_value(get(form_data, 'smoking_status')),                           # 24. Smoking Frequency
            map_value(get(form_data, 'sleep_quality')),                            # 25. Sleep Quality
            map_value(get(form_data, 'physical_activity')),                        # 26. Physical Activity
            map_value(get(form_data, 'masturbation_method')),                      # 27. Masturbation Method
            map_value(get(form_data, 'masturbation_grip')),                        # 28. Masturbation Grip
            map_value(get(form_data, 'masturbation_frequency')),                   # 29. Masturbation Frequency
            map_value(get(form_data, 'porn_frequency')),                           # 30. Porn Usage Frequency
            get_mapped_or_na('partner_response', has_partner),                     # 31. Partner Response (N/A if single)
            get_mapped_or_na('ed_gets_erections', has_ed),                         # 32. ED - Gets Erections (N/A if PE only)
            get_mapped_or_na('ed_sexual_activity_status', has_ed),                 # 33. ED - Sexual Activity Status
            get_mapped_or_na('ed_partner_arousal_speed', has_ed and ed_has_partner_data),  # 34. ED - Arousal Speed (Partner)
            get_mapped_or_na('ed_partner_maintenance', has_ed and ed_has_partner_data),    # 35. ED - Maintenance (Partner)
            get_mapped_or_na('ed_partner_hardness', has_ed and ed_has_partner_data),       # 36. ED - Hardness (Partner)
            get_mapped_or_na('ed_morning_erections', has_ed and ed_has_partner_data),      # 37. ED - Morning Erections
            get_mapped_or_na('ed_masturbation_imagination', has_ed and ed_has_partner_data), # 38. ED - Masturbation/Imagination
            get_mapped_or_na('ed_solo_morning_erections', has_ed and not ed_has_partner_data), # 39. ED - Morning Erections (Solo)
            get_mapped_or_na('ed_solo_masturbation_imagination', has_ed and not ed_has_partner_data), # 40. ED - Masturbation/Imagination (Solo)
            get_mapped_or_na('ed_solo_arousal_speed', has_ed and not ed_has_partner_data),   # 41. ED - Arousal Speed (Solo)
            get_mapped_or_na('pe_sexual_activity_status', has_pe),                 # 42. PE - Sexual Activity Status (N/A if ED only)
            get_mapped_or_na('pe_partner_time_to_ejaculation', has_pe and pe_has_partner_data),  # 43. PE - Ejaculation Time (Partner)
            get_mapped_or_na('pe_partner_type', has_pe and pe_has_partner_data),             # 44. PE - Lifelong/Acquired (Partner)
            get_mapped_or_na('pe_partner_penile_sensitivity', has_pe and pe_has_partner_data), # 45. PE - Penile Sensitivity (Partner)
            get_mapped_or_na('pe_partner_masturbation_control', has_pe and pe_has_partner_data), # 46. PE - Masturbation Control (Partner)
            get_mapped_or_na('pe_solo_time_to_ejaculation', has_pe and not pe_has_partner_data), # 47. PE - Ejaculation Time (Solo)
            get_mapped_or_na('pe_solo_type', has_pe and not pe_has_partner_data),               # 48. PE - Lifelong/Acquired (Solo)
            get_mapped_or_na('pe_solo_penile_sensitivity', has_pe and not pe_has_partner_data),  # 49. PE - Penile Sensitivity (Solo)
            get_mapped_or_na('pe_partner_control', has_pe and not pe_has_partner_data),          # 50. PE - Masturbation Control (Solo)
            get(form_data, 'additional_info'),                                     # 51. Other Information

            # ============================================================
            # SECTION C: AI Output (Columns 52-59)
            # ============================================================
            get(primary_cause, 'category'),                                 # 52. Primary Root Cause - Medical Term
            get(primary_cause, 'explanation'),                              # 53. Primary Root Cause - Explanation
            get(secondary_cause, 'category'),                               # 54. Secondary Root Cause - Medical Term
            get(secondary_cause, 'explanation'),                            # 55. Secondary Root Cause - Explanation
            get(analysis_result, 'detailed_analysis') if analysis_result else "",  # 56. Agent Script
            get(analysis_result, 'summary') if analysis_result else "",     # 57. Treatment Plan
            red_flags_count,                                                # 58. Red Flags Detected
            red_flags_details,                                              # 59. Red Flag Details

            # ============================================================
            # SECTION D: Doctor Review (Columns 60-65)
            # ============================================================
            "Pending",                                                      # 60. Review Status
            "",                                                             # 61. Doctor Name
            "",                                                             # 62. Review Date
            "",                                                             # 63. Doctor Comments
            "",                                                             # 64. Correct Primary Diagnosis
            "",                                                             # 65. Correct Secondary Diagnosis

            # ============================================================
            # SECTION E: System Metadata (Columns 66-71)
            # ============================================================
            self._get_rag_sources(rag_result),                              # 66. RAG Sources Used
            get(primary_cause, 'confidence'),                               # 67. Primary Confidence (%)
            get(secondary_cause, 'confidence'),                             # 68. Secondary Confidence (%)
            round(processing_time_ms / 1000, 2) if processing_time_ms else "",  # 69. Processing Time (sec)
            "hinglish",                                                     # 70. Language Used
            self._format_complete_json(form_data)                           # 71. Complete Form Data (JSON)
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

    def _get_rag_sources(self, rag_result: Optional[Dict[str, Any]]) -> str:
        """
        Extract RAG source chunk IDs.

        Args:
            rag_result: RAG result dictionary

        Returns:
            Comma-separated list of chunk IDs, or empty string
        """
        if not rag_result or not isinstance(rag_result, dict):
            return ""

        chunks = rag_result.get('chunks', [])
        if not chunks or not isinstance(chunks, list):
            return ""

        chunk_ids = []
        for chunk in chunks:
            if isinstance(chunk, dict) and 'chunk_id' in chunk:
                chunk_ids.append(str(chunk['chunk_id']))

        return ", ".join(chunk_ids) if chunk_ids else ""

    def _format_complete_json(self, form_data: Any) -> str:
        """
        Format complete form data as JSON string.

        Args:
            form_data: Form data (dict or object)

        Returns:
            JSON string of form data
        """
        try:
            if isinstance(form_data, dict):
                return json.dumps(form_data, ensure_ascii=False)
            elif hasattr(form_data, '__dict__'):
                return json.dumps(form_data.__dict__, ensure_ascii=False)
            else:
                return str(form_data)
        except Exception as e:
            logger.warning(f"Failed to format form data as JSON: {str(e)}")
            return ""


# Singleton instance
sheets_service = SheetsService()
