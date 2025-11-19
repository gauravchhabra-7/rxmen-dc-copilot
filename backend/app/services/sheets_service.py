"""
Google Sheets logging service.

Logs form submissions and AI analysis results to Google Sheets for tracking and review.
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime, timezone, timedelta
import os
import json
from app.config import settings

logger = logging.getLogger(__name__)

# Google Sheets configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Value mapping dictionary - converts backend codes to user-friendly form text
# Updated to match exact option labels from questions.json
VALUE_MAPPINGS = {
    # Yes/No mappings
    "yes": "Yes",
    "no": "No",
    "true": "Yes",
    "false": "No",

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

    # First Consultation
    "yes_first_time": "Yes (first time seeking treatment)",
    "no_tried_before": "No (has tried treatment before)",

    # Previous Treatments
    "tablets": "Tablets (oral medication)",
    "gels_sprays": "Gels / Sprays (topical)",
    "ayurvedic_homeopathy": "Ayurvedic / Homeopathy",
    "therapy": "Therapy / Counseling",
    "none": "None",

    # Emergency Red Flags
    "severe_pain": "Severe pain in penis/testicles",
    "blood": "Blood in urine or semen",
    "priapism": "Erection lasting more than 4 hours",
    "none": "None of these symptoms",

    # Main Issue
    "ed": "Erectile Dysfunction (ED)",
    "pe": "Premature Ejaculation (PE)",
    "both": "Both ED and PE",

    # Issue Duration
    "lifelong": "Since my first sexual experience (Lifelong)",
    "less_1_month": "Less than 1 month ago",
    "1_to_6_months": "1-6 months ago",
    "6_to_12_months": "6-12 months ago",
    "1_to_3_years": "1-3 years ago",
    "more_3_years": "More than 3 years ago",

    # Issue Context
    "sex_with_partner": "During sex with partner",
    "masturbation": "During masturbation",
    "both_contexts": "Both (during sex and masturbation)",
    "both": "Both (during sex and masturbation)",

    # Medical Conditions
    "diabetes": "Diabetes",
    "hypertension": "High Blood Pressure",
    "high_blood_pressure": "High Blood Pressure",
    "thyroid": "Thyroid disorder",
    "heart_disease": "Heart disease",
    "depression": "Depression",
    "other": "Other (please specify)",

    # Current Medications
    "psychiatric": "Psychiatric medications",
    "blood_pressure": "Blood pressure medications",
    "diabetes_meds": "Diabetes medications",
    "blood_thinners": "Blood thinners",

    # Spinal/Genital Surgery
    "yes": "Yes",
    "no": "No",

    # Alcohol Consumption
    "no_alcohol": "No alcohol",
    "monthly": "Monthly or less",
    "monthly_or_less": "Monthly or less",
    "2_4_monthly": "2-4 times per month",
    "2_3_weekly": "2-3 times per week",
    "2_3_per_week": "2-3 times per week",
    "few_per_week": "Few times per week",
    "4_plus_weekly": "4+ times per week",

    # Smoking Status
    "never": "Never",
    "rarely": "Rarely (social occasions)",
    "rarely_social": "Rarely (social occasions)",
    "sometimes": "Sometimes (few times a month)",
    "sometimes_monthly": "Sometimes (few times a month)",
    "regularly": "Regularly (daily or almost daily)",
    "regularly_daily": "Regularly (daily or almost daily)",

    # Sleep Quality
    "very_poor": "Very poor",
    "poor": "Poor",
    "average": "Average",
    "good": "Good",
    "excellent": "Excellent",

    # Masturbation Method
    "hands": "Hands (normal grip)",
    "hands_normal": "Hands (normal grip)",
    "tight_grip": "Hands (tight/death grip)",
    "hands_tight": "Hands (tight/death grip)",
    "pillow": "Pillow/object rubbing",
    "pillow_rubbing": "Pillow/object rubbing",
    "prone": "Prone (lying face down)",
    "no_masturbation": "No masturbation",
    "none": "No masturbation",

    # Masturbation Frequency
    "never": "Never",
    "1_2_weekly": "1-2 times per week",
    "3_7_weekly": "3-7 times per week",
    "3_to_7": "3-7 times per week",
    "multiple_daily": "Multiple times per day",

    # Porn Frequency
    "never": "Never",
    "rarely": "Rarely (once a month or less)",
    "rarely_monthly": "Rarely (once a month or less)",
    "sometimes": "Sometimes (2-3 times a month)",
    "sometimes_monthly": "Sometimes (2-3 times a month)",
    "regularly": "Regularly (3-5 times a week)",
    "regularly_weekly": "Regularly (3-5 times a week)",
    "3_to_5": "3-5 times per week",
    "daily": "Daily or multiple times per day",
    "daily_or_more": "Daily or multiple times per day",

    # Partner Response
    "supportive": "Supportive",
    "neutral": "Neutral",
    "non_supportive": "Non-supportive",
    "unaware": "Unaware (haven't told them)",

    # ED - Gets Erections
    "yes": "Yes",
    "no": "No",

    # ED - Sexual Activity Status
    "yes_active": "Yes, I have sex with a partner",
    "yes_has_sex": "Yes, I have sex with a partner",
    "avoiding_due_to_fear": "I have a partner but avoid sex due to worry/fear",
    "avoids_due_to_fear": "I have a partner but avoid sex due to worry/fear",
    "no_partner": "No, I do not have a partner",

    # ED - Arousal Speed
    "always": "Always",
    "sometimes": "Sometimes",
    "rarely": "Rarely",

    # ED - Maintenance
    "loses_before_penetration": "Loses hardness before penetration",
    "loses_during_sex": "Stays hard till penetration then loses it",
    "stays_till_completion": "Stays hard till completion",

    # ED - Hardness
    "always_hard": "Always",
    "always": "Always",
    "sometimes_hard": "Sometimes",
    "rarely_hard": "Rarely",
    "never_hard": "Never",
    "never": "Never",

    # ED - Morning Erections
    "regular": "Regular (most mornings)",
    "occasional": "Occasional (sometimes)",
    "absent": "Absent (rarely or never)",

    # ED - Masturbation/Imagination
    "both": "Yes, during both masturbation and imagination",
    "both_work": "Yes, during both masturbation and imagination",
    "masturbation_only": "Yes, during masturbation only",
    "imagination_only": "Yes, with imagination/fantasies only",
    "neither": "No, neither works",

    # PE - Sexual Activity Status (same as ED)
    "yes_active": "Yes, I have sex with a partner",
    "yes_has_sex": "Yes, I have sex with a partner",
    "avoiding_due_to_fear": "I have a partner but avoid sex due to worry/fear",
    "avoids_due_to_fear": "I have a partner but avoid sex due to worry/fear",
    "no_partner": "No, I do not have a partner",

    # PE - Ejaculation Time
    "before_penetration": "Before penetration",
    "less_than_1_min": "Less than 1 minute after penetration",
    "1_to_3_min": "1-3 minutes after penetration",
    "more_than_3_min": "More than 3 minutes",

    # PE - Type (Lifelong vs Acquired)
    "lifelong": "Since first time (lifelong)",
    "acquired": "Started later (acquired)",

    # PE - Penile Sensitivity
    "yes": "Yes",
    "no": "No",

    # PE - Masturbation Control
    "always": "Always",
    "sometimes": "Sometimes",
    "rarely": "Rarely",
    "always_control": "Always",
    "sometimes_control": "Sometimes",
    "rarely_control": "Rarely",
}


def get_ist_timestamp():
    """
    Get current timestamp in IST (Indian Standard Time, UTC+5:30).

    Returns:
        Formatted timestamp string in IST (DD-MM-YYYY HH:MM AM/PM)
    """
    utc_now = datetime.now(timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_now + ist_offset
    return ist_time.strftime("%d-%m-%Y %I:%M %p")


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
        # Context-aware handling for "none" in lists
        if len(value) == 1 and str(value[0]).lower() == 'none':
            # For emergency_red_flags, return the full text
            if field_name == 'emergency_red_flags':
                return 'None of these symptoms'
            # For medical_conditions and current_medications, return "None"
            return 'None'
        mapped = [VALUE_MAPPINGS.get(str(v).lower(), str(v)) for v in value]
        return ', '.join(mapped)

    # Convert to string and check mapping
    value_str = str(value).lower()

    # Context-aware handling for "none" as string
    if value_str == 'none':
        if field_name == 'emergency_red_flags':
            return 'None of these symptoms'
        elif field_name in ['medical_conditions', 'current_medications']:
            return 'None'
        elif field_name == 'masturbation_method':
            return 'No masturbation'

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
        """Initialize spreadsheet headers (65 columns)."""
        headers = [
            # ============================================================
            # Session Metadata (Columns 1-4)
            # ============================================================
            "Session ID",
            "Submission Timestamp",
            "Tester/Agent Name",
            "Form Completion Time (seconds)",

            # ============================================================
            # Patient Input Data (Columns 5-45) - 41 columns
            # ============================================================

            # Section 1: Client Information (10 columns)
            "Full Name",
            "Age",
            "Height",
            "Weight (kg)",
            "City",
            "User's occupation",
            "User's relationship status",
            "First consultation for this issue?",
            "What was tried earlier?",
            "Does user have any of these right now?",

            # Section 2: Main Concern (3 columns)
            "What is the main issue?",
            "Since when are you facing this?",
            "When is the problem faced?",

            # Section 3: Medical & Lifestyle (8 columns)
            "Do you have any chronic medical conditions?",
            "Other chronic medical conditions (specify)",
            "Are you currently taking any medications?",
            "Other current medications (specify)",
            "Any previous spinal or genital surgery or injury?",
            "How often do you drink alcohol?",
            "How often do you smoke?",
            "How would you rate your sleep quality?",

            # Section 4: Masturbation & Behavioral History (4 columns)
            "What is your usual masturbation method?",
            "How often do you masturbate?",
            "How often do you watch porn?",
            "How does your partner respond to the issue?",

            # Section 5: ED Branch (7 columns)
            "Do you get erections at all?",
            "Do you currently have sex with a partner? (ED)",
            "Does it take a long time to get erections?",
            "Does it stay hard till penetration or completion?",
            "Is the erection hard enough for penetration?",
            "Are morning erections regular, occasional, or absent?",
            "Do you get erections during masturbation or with imagination/fantasies?",

            # Section 5: PE Branch (5 columns)
            "Do you currently have sex with a partner? (PE)",
            "What is your ejaculation time during sex?",
            "Has this been since your first sexual encounter or started later?",
            "Do you feel the penis tip is very sensitive?",
            "Can you delay or control ejaculation during masturbation?",

            # Section 6: Other Information (1 column)
            "Other Information",

            # ============================================================
            # AI Analysis Output (Columns 46-53) - 8 columns
            # ============================================================
            "Primary Root Cause - Medical Term",
            "Primary Root Cause - Simple Term",
            "Secondary Root Cause - Medical Term",
            "Secondary Root Cause - Simple Term",
            "Root Cause Explanation",
            "Treatment Explanation",
            "Red Flags Detected",
            "Red Flag Details",

            # ============================================================
            # Doctor Review (Columns 54-59) - 6 columns
            # ============================================================
            "Review Status",
            "Doctor Name",
            "Review Date",
            "Doctor Comments",
            "Correct Primary Diagnosis",
            "Correct Secondary Diagnosis",

            # ============================================================
            # System Metadata (Columns 60-65) - 6 columns
            # ============================================================
            "RAG Sources Used",
            "Primary Confidence (%)",
            "Secondary Confidence (%)",
            "Processing Time (sec)",
            "Language Used",
            "Complete Form Data (JSON)"
        ]

        try:
            self.worksheet.update('A1:BM1', [headers])  # 65 columns = BM
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

            # Prepare row data (65 columns)
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
        Prepare a row of data for Google Sheets (65 columns).

        Column structure:
        - Columns 1-4: Session metadata
        - Columns 5-45: Patient input (41 questions from questions.json)
        - Columns 46-53: AI output (8 columns)
        - Columns 54-59: Doctor review (6 columns)
        - Columns 60-65: System metadata (6 columns)

        Returns:
            List of 65 values corresponding to the header columns
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

        # WEIGHT: Try both 'weight' and 'weight_kg'
        weight_value = get(form_data, 'weight_kg') or get(form_data, 'weight', '')

        # HEIGHT CONVERSION: Convert ft+in to cm if height_cm is not provided
        height_cm = get(form_data, 'height_cm')
        height_ft = get(form_data, 'height_ft')
        height_in = get(form_data, 'height_in')

        # If height_cm is not provided or is empty/zero, try to convert from ft+in
        if (not height_cm or height_cm == '' or height_cm == 0) and height_ft and height_in:
            try:
                # Convert to float and ensure valid values
                ft_val = float(height_ft) if height_ft else 0
                in_val = float(height_in) if height_in else 0

                if ft_val > 0 or in_val > 0:
                    # Convert: 1 foot = 30.48 cm, 1 inch = 2.54 cm
                    total_cm = (ft_val * 30.48) + (in_val * 2.54)
                    height_cm = round(total_cm, 2)
                    logger.info(f"✓ Converted height: {ft_val}ft {in_val}in = {height_cm}cm")
                else:
                    height_cm = ''
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Could not convert height: {e}")
                height_cm = ''

        # Ensure height_cm is not zero
        if height_cm == 0:
            height_cm = ''

        # Debug: Log if critical fields are missing from payload (not just empty)
        # Note: After fix, all fields should be sent from frontend
        if 'full_name' not in form_data:
            logger.debug("Field 'full_name' not in form_data payload")
        if 'city' not in form_data:
            logger.debug("Field 'city' not in form_data payload")
        if 'occupation' not in form_data:
            logger.debug("Field 'occupation' not in form_data payload")

        # Determine conditional N/A logic with proper error handling
        main_issue = str(get(form_data, 'main_issue', '')).lower()
        has_ed = main_issue in ['ed', 'both']
        has_pe = main_issue in ['pe', 'both']

        relationship_status = str(get(form_data, 'relationship_status', '')).lower()
        has_partner = relationship_status in ['married', 'in_relationship']

        # ED pathway logic
        # Partner pathway: User has partner AND gets erections (even if rarely)
        # Solo pathway: User is single OR doesn't get erections at all
        ed_gets_erections = str(get(form_data, 'ed_gets_erections', '')).lower()
        ed_sexual_activity = str(get(form_data, 'ed_sexual_activity_status', '')).lower()

        # User follows partner pathway if:
        # 1. They have a partner (married/in_relationship) AND
        # 2. They get some erections (even if "rarely") AND
        # 3. They are sexually active or avoiding due to fear
        # If ed_gets_erections = "no", then solo pathway regardless of relationship
        ed_has_partner_data = (
            has_partner and
            ed_gets_erections == 'yes' and
            ed_sexual_activity in ['yes_active', 'avoiding_due_to_fear', '']
        )

        # PE pathway logic
        # Partner pathway: User has partner AND sexually active
        # Solo pathway: Not collected in form (always N/A)
        pe_sexual_activity = str(get(form_data, 'pe_sexual_activity_status', '')).lower()
        pe_has_partner_data = (
            has_partner and
            pe_sexual_activity in ['yes_active', 'avoiding_due_to_fear']
        )

        # Masturbation-specific fields (only show if user masturbates)
        masturbation_method = str(get(form_data, 'masturbation_method', '')).lower()
        does_masturbate = masturbation_method not in ['', 'none', 'no_masturbation']

        # First consultation logic
        first_consultation_value = str(get(form_data, 'first_consultation', '')).lower()
        is_first_time = first_consultation_value in ['yes', 'yes_first_time']

        # Helper function to get value with mapping or N/A
        def get_mapped_or_na(key, condition=True, field_name=None):
            """Get field value, apply mapping, or return N/A if condition not met."""
            if not condition:
                return 'N/A'
            value = get(form_data, key, '')
            return map_value(value, field_name) if value != '' else ''

        # Helper to get "other" specify fields with N/A for empty values
        def get_other_or_na(key):
            """Get 'other' specify field value or N/A if empty."""
            value = get(form_data, key, '')
            return value if value else 'N/A'

        # Prepare row data (65 columns in EXACT order matching Google Sheet)
        row = [
            # ============================================================
            # SECTION A: Session Metadata (Columns 1-4)
            # ============================================================
            get(form_data, 'session_id'),                                           # 1. Session ID
            get(form_data, 'submitted_at', get_ist_timestamp()),                   # 2. Submission Timestamp
            get(form_data, 'tester_name'),                                         # 3. Tester/Agent Name
            get(form_data, 'completion_time_seconds'),                             # 4. Form Completion Time (sec)

            # ============================================================
            # SECTION B: Patient Input Data (Columns 5-45) - 41 columns
            # ============================================================

            # Section 1: Client Information (10 columns)
            get(form_data, 'full_name'),                                           # 5. Full Name
            map_value(get(form_data, 'age')),                                      # 6. Age
            map_value(height_cm),                                                  # 7. Height (converted to cm)
            map_value(weight_value),                                               # 8. Weight (kg) - uses weight or weight_kg
            get(form_data, 'city'),                                                # 9. City
            map_value(get(form_data, 'occupation')),                               # 10. User's occupation
            map_value(get(form_data, 'relationship_status')),                      # 11. User's relationship status
            map_value(get(form_data, 'first_consultation')),                       # 12. First consultation for this issue?
            get_mapped_or_na('previous_treatments', not is_first_time),            # 13. What was tried earlier? (N/A if first time)
            map_value(get(form_data, 'emergency_red_flags'), 'emergency_red_flags'),  # 14. Does user have any of these right now?

            # Section 2: Main Concern (3 columns)
            map_value(get(form_data, 'main_issue')),                               # 15. What is the main issue?
            map_value(get(form_data, 'issue_duration')),                           # 16. Since when are you facing this?
            map_value(get(form_data, 'issue_context')),                            # 17. When is the problem faced?

            # Section 3: Medical & Lifestyle (8 columns)
            map_value(get(form_data, 'medical_conditions'), 'medical_conditions'),     # 18. Do you have any chronic medical conditions?
            get_other_or_na('medical_conditions_other'),                               # 19. Other chronic medical conditions (specify) - N/A if empty
            map_value(get(form_data, 'current_medications'), 'current_medications'),   # 20. Are you currently taking any medications?
            get_other_or_na('current_medications_other'),                              # 21. Other current medications (specify) - N/A if empty
            map_value(get(form_data, 'spinal_genital_surgery')),                       # 22. Any previous spinal or genital surgery or injury?
            map_value(get(form_data, 'alcohol_consumption')),                          # 23. How often do you drink alcohol?
            map_value(get(form_data, 'smoking_status')),                               # 24. How often do you smoke?
            map_value(get(form_data, 'sleep_quality')),                                # 25. How would you rate your sleep quality?

            # Section 4: Masturbation & Behavioral History (4 columns)
            map_value(get(form_data, 'masturbation_method'), 'masturbation_method'),   # 26. What is your usual masturbation method?
            map_value(get(form_data, 'masturbation_frequency')),                       # 27. How often do you masturbate?
            map_value(get(form_data, 'porn_frequency')),                               # 28. How often do you watch porn?
            get_mapped_or_na('partner_response', has_partner),                         # 29. How does your partner respond to the issue? (N/A if single)

            # Section 5: ED Branch (7 columns)
            get_mapped_or_na('ed_gets_erections', has_ed),                         # 30. Do you get erections at all? (N/A if PE only)
            get_mapped_or_na('ed_sexual_activity_status', has_ed),                 # 31. Do you currently have sex with a partner? (ED)
            get_mapped_or_na('ed_partner_arousal_speed', has_ed and ed_has_partner_data),  # 32. Does it take a long time to get erections?
            get_mapped_or_na('ed_partner_maintenance', has_ed and ed_has_partner_data),    # 33. Does it stay hard till penetration or completion?
            get_mapped_or_na('ed_partner_hardness', has_ed and ed_has_partner_data),       # 34. Is the erection hard enough for penetration?
            get_mapped_or_na('ed_morning_erections', has_ed),                      # 35. Are morning erections regular, occasional, or absent?
            get_mapped_or_na('ed_masturbation_imagination', has_ed),               # 36. Do you get erections during masturbation or with imagination/fantasies?

            # Section 5: PE Branch (5 columns)
            get_mapped_or_na('pe_sexual_activity_status', has_pe),                 # 37. Do you currently have sex with a partner? (PE)
            get_mapped_or_na('pe_partner_ejaculation_time', has_pe),               # 38. What is your ejaculation time during sex?
            get_mapped_or_na('pe_partner_type', has_pe),                           # 39. Has this been since your first sexual encounter or started later?
            get_mapped_or_na('pe_partner_penile_sensitivity', has_pe),             # 40. Do you feel the penis tip is very sensitive?
            get_mapped_or_na('pe_partner_masturbation_control', has_pe),           # 41. Can you delay or control ejaculation during masturbation?

            # Section 6: Other Information (1 column)
            get(form_data, 'additional_information'),                              # 42. Other Information

            # ============================================================
            # SECTION C: AI Output (Columns 46-53) - 8 columns
            # ============================================================
            get(primary_cause, 'category'),                                            # 46. Primary Root Cause - Medical Term
            get(primary_cause, 'simple_term'),                                         # 47. Primary Root Cause - Simple Term
            get(secondary_cause, 'category'),                                          # 48. Secondary Root Cause - Medical Term
            get(secondary_cause, 'simple_term'),                                       # 49. Secondary Root Cause - Simple Term
            get(analysis_result, 'root_cause_explanation') if analysis_result else "", # 50. Root Cause Explanation
            get(analysis_result, 'treatment_explanation') if analysis_result else "",  # 51. Treatment Explanation
            red_flags_count,                                                           # 52. Red Flags Detected
            red_flags_details,                                                         # 53. Red Flag Details

            # ============================================================
            # SECTION D: Doctor Review (Columns 54-59) - 6 columns
            # ============================================================
            "Pending",                                                             # 54. Review Status
            "",                                                                    # 55. Doctor Name
            "",                                                                    # 56. Review Date
            "",                                                                    # 57. Doctor Comments
            "",                                                                    # 58. Correct Primary Diagnosis
            "",                                                                    # 59. Correct Secondary Diagnosis

            # ============================================================
            # SECTION E: System Metadata (Columns 60-65) - 6 columns
            # ============================================================
            self._get_rag_sources(rag_result),                                     # 60. RAG Sources Used
            get(primary_cause, 'confidence'),                                      # 61. Primary Confidence (%)
            get(secondary_cause, 'confidence'),                                    # 62. Secondary Confidence (%)
            round(processing_time_ms / 1000, 2) if processing_time_ms else "",     # 63. Processing Time (sec)
            "hinglish",                                                            # 64. Language Used
            self._format_complete_json(form_data)                                  # 65. Complete Form Data (JSON)
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
