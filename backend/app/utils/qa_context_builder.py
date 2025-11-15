"""
Q&A Context Builder.

Transforms form data into question-answer pairs for personalized AI responses.
"""

from typing import Dict, List, Any


# Question mapping for all form fields
QUESTION_MAP = {
    # Section 1: Client Information
    "age": "What is your age?",
    "height_cm": "What is your height?",
    "height_ft": "What is your height in feet?",
    "height_in": "What is your height in inches?",
    "weight": "What is your weight?",

    # Section 2: Main Concern
    "main_issue": "What is your main concern?",
    "emergency_red_flags": "Do you have any of these emergency symptoms?",

    # Section 3: Medical & Lifestyle
    "medical_conditions": "Do you have any chronic medical conditions?",
    "current_medications": "Are you currently taking any medications?",
    "spinal_genital_surgery": "Have you had any spinal or genital surgery or injury?",
    "alcohol_consumption": "How often do you consume alcohol?",
    "smoking_status": "Do you smoke?",
    "substance_consumption": "Do you use any other substances?",
    "sleep_quality": "How is your sleep quality?",
    "physical_activity": "How often do you exercise or engage in physical activity?",

    # Section 4: Masturbation & Behavioral History
    "relationship_status": "What is your relationship status?",
    "masturbation_method": "How do you typically masturbate?",
    "masturbation_grip": "What type of grip do you use?",
    "masturbation_frequency": "How often do you masturbate?",
    "porn_frequency": "How often do you watch pornography?",
    "partner_response": "How does your partner respond to this issue?",

    # Section 5: ED Branch
    "ed_gets_erections": "Do you get erections at all?",
    "ed_sexual_activity_status": "Are you currently sexually active with a partner?",
    "ed_partner_arousal_speed": "How long does it take to get an erection with your partner?",
    "ed_partner_maintenance": "Can you maintain the erection during sex?",
    "ed_partner_hardness": "How would you describe the hardness of your erection?",
    "ed_morning_erections": "Do you get morning erections?",
    "ed_masturbation_imagination": "Do you get erections during masturbation or when thinking about sex?",

    # Section 6: PE Branch
    "pe_sexual_activity_status": "Are you currently sexually active with a partner?",
    "pe_partner_time_to_ejaculation": "How long does it take before you ejaculate with your partner?",
    "pe_partner_control": "How much control do you have over ejaculation during partnered sex?",
    "pe_partner_satisfaction": "Are you and your partner satisfied with the duration?",
    "pe_partner_masturbation_control": "How much control do you have during masturbation?",

    # Section 7: Other
    "first_consultation": "Is this your first consultation for this issue?",
    "previous_treatments": "What treatments have you tried before?",
    "additional_info": "Is there anything else you'd like to share?",
}


def format_answer(field_name: str, value: Any) -> str:
    """
    Format the answer value into a human-readable string.

    Args:
        field_name: Name of the form field
        value: Raw value from form

    Returns:
        Formatted answer string
    """
    if value is None:
        return "Not answered"

    # Handle lists (checkboxes)
    if isinstance(value, list):
        if not value or value == ["none"]:
            return "None"
        return ", ".join(value)

    # Handle booleans
    if isinstance(value, bool):
        return "Yes" if value else "No"

    # Handle numbers
    if isinstance(value, (int, float)):
        if field_name == "age":
            return f"{value} years old"
        elif field_name in ["height_cm"]:
            return f"{value} cm"
        elif field_name == "weight":
            return f"{value} kg"
        else:
            return str(value)

    # Handle strings - convert underscores to spaces and capitalize
    if isinstance(value, str):
        # Common value mappings for better readability
        value_map = {
            "ed": "Erectile Dysfunction (ED)",
            "pe": "Premature Ejaculation (PE)",
            "both": "Both ED and PE",
            "none": "None",
            "never": "Never",
            "yes": "Yes",
            "no": "No",
            "once_week": "Once a week",
            "once_month": "Once a month",
            "daily": "Daily",
            "3_to_5": "3-5 times per week",
            "3_to_7": "3-7 times per week",
            "less_1_min": "Less than 1 minute",
            "1_2_min": "1-2 minutes",
            "2_5_min": "2-5 minutes",
            "hands": "Using hands",
            "tight": "Tight grip",
            "normal": "Normal grip",
            "good": "Good",
            "poor": "Poor",
            "moderate": "Moderate",
            "married": "Married",
            "in_relationship": "In a relationship",
            "single": "Single",
            "divorced": "Divorced",
        }

        return value_map.get(value.lower(), value.replace("_", " ").title())

    return str(value)


def build_qa_context(form_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Build question-answer context from form data.

    Args:
        form_data: Raw form data dictionary

    Returns:
        List of Q&A pairs with field names
    """
    qa_pairs = []

    for field_name, value in form_data.items():
        # Skip metadata fields and None values
        if field_name in ["form_version", "submitted_at"]:
            continue

        # Skip if no question mapping exists
        if field_name not in QUESTION_MAP:
            continue

        # Skip empty values (but include 0, False)
        if value is None or value == "" or value == []:
            continue

        question = QUESTION_MAP[field_name]
        answer = format_answer(field_name, value)

        qa_pairs.append({
            "field_name": field_name,
            "question": question,
            "answer": answer
        })

    return qa_pairs


def format_qa_context_for_prompt(qa_pairs: List[Dict[str, str]]) -> str:
    """
    Format Q&A pairs into a readable prompt section.

    Args:
        qa_pairs: List of question-answer dictionaries

    Returns:
        Formatted string for prompt
    """
    if not qa_pairs:
        return "No patient context available."

    sections = {
        "demographics": [],
        "main_concern": [],
        "medical_lifestyle": [],
        "behavioral": [],
        "ed_specific": [],
        "pe_specific": [],
        "other": []
    }

    # Categorize Q&A pairs
    for qa in qa_pairs:
        field = qa["field_name"]

        if field in ["age", "height_cm", "height_ft", "height_in", "weight"]:
            sections["demographics"].append(qa)
        elif field in ["main_issue", "emergency_red_flags"]:
            sections["main_concern"].append(qa)
        elif field in ["medical_conditions", "current_medications", "spinal_genital_surgery",
                       "alcohol_consumption", "smoking_status", "substance_consumption",
                       "sleep_quality", "physical_activity"]:
            sections["medical_lifestyle"].append(qa)
        elif field in ["relationship_status", "masturbation_method", "masturbation_grip",
                       "masturbation_frequency", "porn_frequency", "partner_response"]:
            sections["behavioral"].append(qa)
        elif field.startswith("ed_"):
            sections["ed_specific"].append(qa)
        elif field.startswith("pe_"):
            sections["pe_specific"].append(qa)
        else:
            sections["other"].append(qa)

    # Build formatted output
    output_parts = ["## PATIENT QUESTION-ANSWER CONTEXT", ""]

    section_titles = {
        "demographics": "### Demographics",
        "main_concern": "### Main Concern",
        "medical_lifestyle": "### Medical History & Lifestyle",
        "behavioral": "### Behavioral Patterns",
        "ed_specific": "### ED-Specific Symptoms",
        "pe_specific": "### PE-Specific Symptoms",
        "other": "### Additional Information"
    }

    for section_key, title in section_titles.items():
        items = sections[section_key]
        if not items:
            continue

        output_parts.append(title)
        output_parts.append("")

        for qa in items:
            output_parts.append(f"**Q: {qa['question']}**")
            output_parts.append(f"A: {qa['answer']}")
            output_parts.append("")

    return "\n".join(output_parts)


def get_diagnostic_highlights(qa_pairs: List[Dict[str, str]], main_issue: str) -> str:
    """
    Extract key diagnostic indicators for the AI to focus on.

    Args:
        qa_pairs: List of Q&A pairs
        main_issue: Main issue (ed/pe/both)

    Returns:
        String highlighting key diagnostic patterns
    """
    highlights = ["## KEY DIAGNOSTIC INDICATORS", ""]

    # Find relevant patterns based on main issue
    qa_dict = {qa["field_name"]: qa["answer"] for qa in qa_pairs}

    # ED patterns
    if main_issue in ["ed", "both"]:
        if "ed_morning_erections" in qa_dict and "ed_partner_maintenance" in qa_dict:
            highlights.append("**Pattern to Note:**")
            highlights.append(f"- Morning erections: {qa_dict.get('ed_morning_erections', 'N/A')}")
            highlights.append(f"- Partner erection maintenance: {qa_dict.get('ed_partner_maintenance', 'N/A')}")
            highlights.append("→ If morning erections are normal but partner performance is poor, consider psychological factors")
            highlights.append("")

    # PE patterns
    if main_issue in ["pe", "both"]:
        if "pe_partner_time_to_ejaculation" in qa_dict and "pe_partner_masturbation_control" in qa_dict:
            highlights.append("**Pattern to Note:**")
            highlights.append(f"- Time with partner: {qa_dict.get('pe_partner_time_to_ejaculation', 'N/A')}")
            highlights.append(f"- Control during masturbation: {qa_dict.get('pe_partner_masturbation_control', 'N/A')}")
            highlights.append("→ If control is better during masturbation, consider performance anxiety or behavioral conditioning")
            highlights.append("")

    # Behavioral patterns
    if "masturbation_grip" in qa_dict and qa_dict["masturbation_grip"] == "Tight grip":
        highlights.append("**Behavioral Pattern:**")
        highlights.append(f"- Uses tight grip during masturbation")
        highlights.append("→ May indicate conditioned arousal pattern requiring desensitization")
        highlights.append("")

    if "porn_frequency" in qa_dict and qa_dict["porn_frequency"] in ["Daily", "3-5 times per week", "3-7 times per week"]:
        highlights.append("**Behavioral Pattern:**")
        highlights.append(f"- Frequent pornography usage: {qa_dict.get('porn_frequency', 'N/A')}")
        highlights.append("→ Consider impact on arousal expectations and partner performance")
        highlights.append("")

    if len(highlights) <= 2:  # Only header
        return ""

    return "\n".join(highlights)
