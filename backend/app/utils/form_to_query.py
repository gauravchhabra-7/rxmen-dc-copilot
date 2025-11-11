"""
Form Data to Search Query Converter.

Converts patient form data into semantic search queries for RAG retrieval.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def form_data_to_query(form_data: Dict[str, Any]) -> str:
    """
    Convert form data to a semantic search query.

    Args:
        form_data: Patient form data dictionary

    Returns:
        Search query string optimized for semantic search
    """
    query_parts = []

    # Main issue
    main_issue = form_data.get("main_issue", "").lower()
    if main_issue == "ed":
        query_parts.append("Erectile dysfunction ED")
    elif main_issue == "pe":
        query_parts.append("Premature ejaculation PE")
    elif main_issue == "both":
        query_parts.append("Erectile dysfunction and premature ejaculation")

    # Medical conditions
    medical_conditions = form_data.get("medical_conditions", [])
    if medical_conditions and medical_conditions != ["none"]:
        conditions_str = " ".join([c for c in medical_conditions if c != "none"])
        if conditions_str:
            query_parts.append(f"medical conditions: {conditions_str}")

    # Behavioral patterns (ED specific)
    if main_issue in ["ed", "both"]:
        # Morning erections indicator
        morning_erections = form_data.get("ed_morning_erections", "")
        if morning_erections in ["rarely", "never", "absent"]:
            query_parts.append("no morning erections")
        elif morning_erections in ["sometimes", "often", "yes"]:
            query_parts.append("has morning erections")

        # Partner vs solo performance
        gets_erections = form_data.get("ed_gets_erections", "")
        masturbation_imagination = form_data.get("ed_masturbation_imagination", "")

        if gets_erections == "yes" and masturbation_imagination in ["yes", "sometimes"]:
            query_parts.append("works during masturbation but fails with partner")
        elif gets_erections == "no":
            query_parts.append("complete erectile failure no erections")

    # Behavioral patterns (PE specific)
    if main_issue in ["pe", "both"]:
        # Control and timing
        partner_time = form_data.get("pe_partner_time_to_ejaculation", "")
        if partner_time in ["less_than_1_min", "1_to_2_min"]:
            query_parts.append("finishes very quickly premature ejaculation")

        partner_control = form_data.get("pe_partner_control", "")
        if partner_control in ["no_control", "minimal_control"]:
            query_parts.append("no control over ejaculation")

    # Masturbation patterns
    masturbation_grip = form_data.get("masturbation_grip", "")
    if masturbation_grip in ["very_tight", "tight"]:
        query_parts.append("tight grip during masturbation")

    masturbation_frequency = form_data.get("masturbation_frequency", "")
    if masturbation_frequency in ["daily", "more_than_once_daily"]:
        query_parts.append("frequent masturbation")

    # Porn usage
    porn_frequency = form_data.get("porn_frequency", "")
    if porn_frequency in ["daily", "5_to_7_per_week"]:
        query_parts.append("high pornography usage")

    # Psychological indicators
    relationship_status = form_data.get("relationship_status", "")
    partner_response = form_data.get("partner_response", "")

    if partner_response in ["frustrated", "disappointed", "upset"]:
        query_parts.append("partner relationship stress performance anxiety")
    elif relationship_status in ["single", "no_partner"]:
        query_parts.append("no current partner")

    # Lifestyle factors
    sleep_quality = form_data.get("sleep_quality", "")
    if sleep_quality in ["poor", "very_poor"]:
        query_parts.append("poor sleep quality")

    physical_activity = form_data.get("physical_activity", "")
    if physical_activity in ["sedentary", "rarely"]:
        query_parts.append("sedentary lifestyle no exercise")

    alcohol = form_data.get("alcohol_consumption", "")
    if alcohol in ["daily", "multiple_times_daily"]:
        query_parts.append("heavy alcohol consumption")

    smoking = form_data.get("smoking_status", "")
    if smoking in ["current_smoker", "heavy_smoker"]:
        query_parts.append("smoking tobacco use")

    # Build final query
    query = " ".join(query_parts)

    logger.info(f"Generated search query: {query[:100]}...")

    return query


def extract_key_symptoms(form_data: Dict[str, Any]) -> List[str]:
    """
    Extract key symptoms as discrete items.

    Args:
        form_data: Patient form data dictionary

    Returns:
        List of key symptom strings
    """
    symptoms = []

    main_issue = form_data.get("main_issue", "").lower()

    if main_issue in ["ed", "both"]:
        if form_data.get("ed_morning_erections") in ["rarely", "never"]:
            symptoms.append("No morning erections")

        if form_data.get("ed_gets_erections") == "no":
            symptoms.append("Cannot achieve erections")

        if form_data.get("ed_partner_maintenance") in ["rarely", "never"]:
            symptoms.append("Cannot maintain erections")

    if main_issue in ["pe", "both"]:
        if form_data.get("pe_partner_time_to_ejaculation") in ["less_than_1_min", "1_to_2_min"]:
            symptoms.append("Very quick ejaculation (<2 min)")

        if form_data.get("pe_partner_control") in ["no_control", "minimal_control"]:
            symptoms.append("No control over ejaculation")

    # Medical conditions
    conditions = form_data.get("medical_conditions", [])
    if "diabetes" in conditions:
        symptoms.append("Diabetes")
    if "hypertension" in conditions:
        symptoms.append("High blood pressure")
    if "cardiovascular_disease" in conditions or "heart_disease" in conditions:
        symptoms.append("Cardiovascular disease")

    return symptoms
