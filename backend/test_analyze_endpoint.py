"""
Test script for /analyze endpoint.

Tests the complete RAG + Claude integration with realistic patient cases.

Run:
    python test_analyze_endpoint.py

Requirements:
    - API server running on http://localhost:8000
    - All API keys configured (.env)
    - Pinecone index populated (31 chunks)
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def test_endpoint_status():
    """Test if the endpoint is accessible."""
    print_header("TEST 0: Endpoint Status Check")

    try:
        response = requests.get(f"{BASE_URL}/analyze/test")
        response.raise_for_status()

        data = response.json()
        print_success("Endpoint is accessible")
        print_info(f"Status: {data.get('status')}")
        print_info(f"Services: {data.get('services')}")

        return True

    except Exception as e:
        print_error(f"Endpoint test failed: {str(e)}")
        return False


def test_performance_anxiety_case():
    """Test Case 1: Performance Anxiety ED."""
    print_header("TEST 1: Performance Anxiety ED")

    test_data = {
        "age": 28,
        "height_cm": 175,
        "weight": 75,
        "main_issue": "ed",
        "emergency_red_flags": "none",
        "medical_conditions": ["none"],
        "current_medications": ["none"],
        "spinal_genital_surgery": "no",
        "alcohol_consumption": "once_week",
        "smoking_status": "never",
        "substance_consumption": "none",
        "sleep_quality": "good",
        "physical_activity": "moderate",
        "relationship_status": "in_relationship",
        "masturbation_method": "hands",
        "masturbation_grip": "normal",
        "masturbation_frequency": "3_to_5",
        "porn_frequency": "3_to_5",
        "partner_response": "frustrated",
        # ED specific
        "ed_gets_erections": "yes",
        "ed_sexual_activity_status": "active",
        "ed_morning_erections": "yes",
        "ed_masturbation_imagination": "yes",
        "ed_partner_arousal_speed": "slow",
        "ed_partner_maintenance": "rarely",
        "ed_partner_hardness": "soft",
        # Other
        "first_consultation": "yes",
        "previous_treatments": [],
        "additional_info": "Works fine during masturbation but fails with partner"
    }

    print_info("Scenario: Works during masturbation, fails with partner")
    print_info("Expected: Performance Anxiety (primary) + Relationship Stress (secondary)")

    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            timeout=120
        )
        response.raise_for_status()

        result = response.json()

        print_success("Analysis completed")
        print_info(f"Primary Diagnosis: {result.get('primary_diagnosis')}")
        print_info(f"Root Causes: {len(result.get('root_causes', []))}")

        for i, cause in enumerate(result.get('root_causes', []), 1):
            print(f"  {i}. {cause.get('category')} ({cause.get('confidence')})")
            print(f"     {cause.get('explanation')[:100]}...")

        print_info(f"Model Used: {result.get('model_used')}")
        print_info(f"Sources: {', '.join(result.get('sources_used', [])[:3])}")

        return True

    except requests.exceptions.Timeout:
        print_error("Request timed out (>30s)")
        return False
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


def test_diabetes_ed_case():
    """Test Case 2: Diabetes-related ED."""
    print_header("TEST 2: Diabetes-Related ED")

    test_data = {
        "age": 45,
        "height_cm": 178,
        "weight": 92,
        "main_issue": "ed",
        "emergency_red_flags": "none",
        "medical_conditions": ["diabetes", "hypertension"],
        "current_medications": ["metformin", "lisinopril"],
        "spinal_genital_surgery": "no",
        "alcohol_consumption": "rarely",
        "smoking_status": "former_smoker",
        "substance_consumption": "none",
        "sleep_quality": "fair",
        "physical_activity": "sedentary",
        "relationship_status": "married",
        "masturbation_method": "hands",
        "masturbation_grip": "normal",
        "masturbation_frequency": "1_to_2",
        "porn_frequency": "1_to_2",
        "partner_response": "understanding",
        # ED specific
        "ed_gets_erections": "sometimes",
        "ed_sexual_activity_status": "active",
        "ed_morning_erections": "rarely",
        "ed_masturbation_imagination": "sometimes",
        "ed_partner_arousal_speed": "very_slow",
        "ed_partner_maintenance": "never",
        "ed_partner_hardness": "very_soft",
        # Other
        "first_consultation": "no",
        "previous_treatments": ["sildenafil"],
        "additional_info": "Gradual onset over 2 years"
    }

    print_info("Scenario: Diabetic patient, no morning erections, gradual onset")
    print_info("Expected: Vascular/Diabetes ED (primary) + Hormonal (secondary)")

    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            timeout=120
        )
        response.raise_for_status()

        result = response.json()

        print_success("Analysis completed")
        print_info(f"Primary Diagnosis: {result.get('primary_diagnosis')}")

        for i, cause in enumerate(result.get('root_causes', []), 1):
            print(f"  {i}. {cause.get('category')} ({cause.get('confidence')})")

        return True

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


def test_premature_ejaculation_case():
    """Test Case 3: Premature Ejaculation."""
    print_header("TEST 3: Premature Ejaculation (PE)")

    test_data = {
        "age": 30,
        "height_cm": 172,
        "weight": 70,
        "main_issue": "pe",
        "emergency_red_flags": "none",
        "medical_conditions": ["none"],
        "current_medications": ["none"],
        "spinal_genital_surgery": "no",
        "alcohol_consumption": "once_week",
        "smoking_status": "never",
        "substance_consumption": "none",
        "sleep_quality": "good",
        "physical_activity": "moderate",
        "relationship_status": "married",
        "masturbation_method": "hands",
        "masturbation_grip": "very_tight",
        "masturbation_frequency": "daily",
        "porn_frequency": "daily",
        "partner_response": "frustrated",
        # PE specific
        "pe_sexual_activity_status": "active",
        "pe_partner_time_to_ejaculation": "less_than_1_min",
        "pe_partner_control": "no_control",
        "pe_partner_satisfaction": "not_satisfied",
        "pe_partner_masturbation_control": "good_control",
        # Other
        "first_consultation": "yes",
        "previous_treatments": [],
        "additional_info": "Tight grip during masturbation, high porn usage"
    }

    print_info("Scenario: Very quick ejaculation, tight grip, high porn usage")
    print_info("Expected: Behavioral (tight grip) + Performance Anxiety")

    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            timeout=120
        )
        response.raise_for_status()

        result = response.json()

        print_success("Analysis completed")
        print_info(f"Primary Diagnosis: {result.get('primary_diagnosis')}")

        for i, cause in enumerate(result.get('root_causes', []), 1):
            print(f"  {i}. {cause.get('category')} ({cause.get('confidence')})")

        return True

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print_header(f"RxMen /analyze Endpoint Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print_info("Prerequisites:")
    print_info("  - API server running on http://localhost:8000")
    print_info("  - All API keys configured in .env")
    print_info("  - Pinecone index populated with 31 chunks")
    print_info("  - System prompt documents loaded")
    print()

    results = []

    # Test 0: Endpoint status
    results.append(("Endpoint Status", test_endpoint_status()))

    if not results[0][1]:
        print_error("\n⚠️ Endpoint not accessible. Please start the API server:")
        print_error("   cd backend && uvicorn app.main:app --reload")
        return 1

    # Test 1: Performance Anxiety
    results.append(("Performance Anxiety ED", test_performance_anxiety_case()))

    # Test 2: Diabetes ED
    results.append(("Diabetes-Related ED", test_diabetes_ed_case()))

    # Test 3: Premature Ejaculation
    results.append(("Premature Ejaculation", test_premature_ejaculation_case()))

    # Summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for _, status in results if status)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print()

    for test_name, status in results:
        status_text = f"{GREEN}✓ PASS{RESET}" if status else f"{RED}✗ FAIL{RESET}"
        print(f"{test_name:30} {status_text}")

    print()

    if passed == total:
        print_success("All tests passed! /analyze endpoint is fully operational.")
        return 0
    else:
        print_error(f"{failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
