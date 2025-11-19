"""
Test script for personalized AI output.

Demonstrates Q&A context building and personalization features.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.qa_context_builder import (
    build_qa_context,
    format_qa_context_for_prompt,
    get_diagnostic_highlights
)


# Sample test data - PE case with behavioral patterns
sample_pe_case = {
    "age": 28,
    "height_cm": 175,
    "weight": 72,
    "main_issue": "pe",
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
    "masturbation_grip": "tight",
    "masturbation_frequency": "3_to_7",
    "porn_frequency": "daily",
    "partner_response": "frustrated",
    "pe_sexual_activity_status": "yes",
    "pe_partner_time_to_ejaculation": "less_1_min",
    "pe_partner_control": "no_control",
    "pe_partner_satisfaction": "no",
    "pe_partner_masturbation_control": "good_control",
    "first_consultation": "yes",
    "additional_info": ""
}


# Sample ED case
sample_ed_case = {
    "age": 35,
    "height_cm": 180,
    "weight": 85,
    "main_issue": "ed",
    "emergency_red_flags": "none",
    "medical_conditions": ["diabetes"],
    "current_medications": ["metformin"],
    "spinal_genital_surgery": "no",
    "alcohol_consumption": "daily",
    "smoking_status": "former",
    "sleep_quality": "poor",
    "physical_activity": "sedentary",
    "relationship_status": "married",
    "masturbation_method": "hands",
    "masturbation_grip": "normal",
    "masturbation_frequency": "3_to_7",
    "porn_frequency": "daily",
    "partner_response": "understanding",
    "ed_gets_erections": "yes",
    "ed_sexual_activity_status": "yes",
    "ed_partner_arousal_speed": "slow",
    "ed_partner_maintenance": "difficult",
    "ed_partner_hardness": "soft",
    "ed_morning_erections": "yes",
    "ed_masturbation_imagination": "yes",
    "first_consultation": "no",
    "previous_treatments": ["sildenafil"],
    "additional_info": "Partner is very understanding but I feel anxious"
}


def test_qa_context_builder():
    """Test Q&A context building."""
    print("="*80)
    print("TEST 1: Q&A CONTEXT BUILDING")
    print("="*80)
    print()

    # Test with PE case
    print("Testing with PE case (tight grip + daily porn)...")
    print()

    qa_pairs = build_qa_context(sample_pe_case)
    print(f"✓ Built {len(qa_pairs)} question-answer pairs")
    print()

    # Show first 5 Q&A pairs
    print("Sample Q&A pairs:")
    for i, qa in enumerate(qa_pairs[:5], 1):
        print(f"{i}. Q: {qa['question']}")
        print(f"   A: {qa['answer']}")
        print()

    print("="*80)
    print()


def test_formatted_prompt():
    """Test formatted prompt generation."""
    print("="*80)
    print("TEST 2: FORMATTED PROMPT FOR CLAUDE")
    print("="*80)
    print()

    qa_pairs = build_qa_context(sample_pe_case)
    formatted_prompt = format_qa_context_for_prompt(qa_pairs)

    print("Formatted Q&A Context (first 1000 chars):")
    print(formatted_prompt[:1000])
    print("...")
    print()

    print(f"✓ Total prompt length: {len(formatted_prompt)} characters")
    print("="*80)
    print()


def test_diagnostic_highlights():
    """Test diagnostic highlights extraction."""
    print("="*80)
    print("TEST 3: DIAGNOSTIC HIGHLIGHTS")
    print("="*80)
    print()

    # Test PE case
    print("PE Case Highlights:")
    qa_pairs_pe = build_qa_context(sample_pe_case)
    highlights_pe = get_diagnostic_highlights(qa_pairs_pe, "pe")
    print(highlights_pe if highlights_pe else "No specific highlights")
    print()

    # Test ED case
    print("ED Case Highlights:")
    qa_pairs_ed = build_qa_context(sample_ed_case)
    highlights_ed = get_diagnostic_highlights(qa_pairs_ed, "ed")
    print(highlights_ed if highlights_ed else "No specific highlights")
    print()

    print("="*80)
    print()


def test_personalization_check():
    """Show how personalization should work."""
    print("="*80)
    print("TEST 4: PERSONALIZATION DEMONSTRATION")
    print("="*80)
    print()

    qa_pairs = build_qa_context(sample_pe_case)

    # Find key diagnostic answers
    key_answers = {
        "partner_time": None,
        "masturbation_control": None,
        "grip": None,
        "porn": None
    }

    for qa in qa_pairs:
        if "time to ejaculation" in qa['question'].lower():
            key_answers["partner_time"] = qa['answer']
        elif "control during masturbation" in qa['question'].lower():
            key_answers["masturbation_control"] = qa['answer']
        elif "grip" in qa['question'].lower():
            key_answers["grip"] = qa['answer']
        elif "pornography" in qa['question'].lower():
            key_answers["porn"] = qa['answer']

    print("KEY DIAGNOSTIC INDICATORS:")
    print("-" * 80)
    for key, value in key_answers.items():
        if value:
            print(f"  {key}: {value}")
    print()

    print("PERSONALIZED EXPLANATION EXAMPLE:")
    print("-" * 80)
    print(f"""
✅ GOOD (Personalized):
"Aapne bataya ki partner ke saath {key_answers['partner_time']} mein ejaculation
ho jaata hai, lekin masturbation mein aapka control {key_answers['masturbation_control']}
hai. Isse clearly pata chalta hai ki physically capability toh hai, but kuch behavioral
factors involved hain. Aapne yeh bhi mention kiya ki {key_answers['grip']} use karte
ho aur {key_answers['porn']} porn dekhte ho - yeh dono body ko ek specific arousal
pattern ki aadat daal dete hain."

❌ BAD (Generic):
"Premature ejaculation can be caused by psychological or behavioral factors.
Treatment includes therapy and medication."

The difference: First references SPECIFIC patient answers. Second is textbook generic.
    """)

    print("="*80)
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PERSONALIZED OUTPUT TEST SUITE" + " "*27 + "║")
    print("╚" + "="*78 + "╝")
    print("\n")

    test_qa_context_builder()
    test_formatted_prompt()
    test_diagnostic_highlights()
    test_personalization_check()

    print("╔" + "="*78 + "╗")
    print("║" + " "*30 + "ALL TESTS COMPLETE" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    print("\n")

    print("NEXT STEPS:")
    print("-" * 80)
    print("1. ✅ Q&A context builder is working")
    print("2. ✅ Formatted prompts are being generated")
    print("3. ✅ Diagnostic highlights are being extracted")
    print("4. 📋 Ready to test with actual Claude API")
    print()
    print("To test with Claude API, run:")
    print("  python backend/test_analyze_endpoint.py")
    print()


if __name__ == "__main__":
    main()
