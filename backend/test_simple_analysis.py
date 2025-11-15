"""
Simple test script for debugging /analyze endpoint.

Tests a single case with detailed logging.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Simple PE test case
test_case = {
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
    "pe_sexual_activity_status": "yes",
    "pe_partner_time_to_ejaculation": "less_1_min",
    "pe_partner_control": "no_control",
    "pe_partner_satisfaction": "no",
    "pe_partner_masturbation_control": "good_control",
    "first_consultation": "yes"
}

def test_analyze():
    """Test the analyze endpoint with detailed output."""

    print("=" * 80)
    print("TESTING /api/v1/analyze ENDPOINT")
    print("=" * 80)
    print()

    print("Test Case: PE with Behavioral Patterns")
    print("-" * 80)
    print("• Main Issue: Premature Ejaculation")
    print("• Time with partner: Less than 1 minute")
    print("• Masturbation control: Good control")
    print("• Grip: Tight grip")
    print("• Porn frequency: Daily")
    print()

    print("Sending request to API...")
    print(f"URL: {BASE_URL}/analyze")
    print(f"Timeout: 120 seconds")
    print()

    try:
        start_time = datetime.now()

        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_case,
            timeout=120,
            headers={"Content-Type": "application/json"}
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✓ Response received in {elapsed:.2f} seconds")
        print()

        if response.status_code == 200:
            result = response.json()

            print("=" * 80)
            print("RESPONSE DATA")
            print("=" * 80)
            print()

            print(f"Success: {result.get('success')}")
            print(f"Primary Diagnosis: {result.get('primary_diagnosis')}")
            print()

            # Root causes
            root_causes = result.get('root_causes', [])
            print(f"Root Causes Found: {len(root_causes)}")
            print("-" * 80)

            for i, cause in enumerate(root_causes, 1):
                print(f"\nROOT CAUSE {i}:")
                print(f"  Category: {cause.get('category')}")
                print(f"  Confidence: {cause.get('confidence')}")
                print(f"  Explanation:")
                print(f"    {cause.get('explanation', 'N/A')}")
                print()

                # Check for personalization
                explanation = cause.get('explanation', '').lower()
                if 'aapne bataya' in explanation or 'aapne mention' in explanation:
                    print(f"  ✓ PERSONALIZATION DETECTED in explanation")
                else:
                    print(f"  ⚠ WARNING: No obvious personalization phrases found")
                print()

            # Treatment
            print("TREATMENT RECOMMENDATION:")
            print("-" * 80)
            treatment = result.get('recommended_actions', [])
            detailed = result.get('detailed_analysis', '')

            if detailed:
                print(detailed[:500])
                if len(detailed) > 500:
                    print("...")
                print()

                # Check treatment personalization
                if 'aapne bataya' in detailed.lower() or 'tight grip' in detailed.lower():
                    print("✓ TREATMENT PERSONALIZATION DETECTED")
                else:
                    print("⚠ WARNING: Treatment may not reference specific patient habits")

            print()
            print("=" * 80)
            print("FULL JSON RESPONSE")
            print("=" * 80)
            print(json.dumps(result, indent=2))

        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print(f"✗ Request timed out after 120 seconds")
        print()
        print("TROUBLESHOOTING:")
        print("1. Check if server logs show 'ANALYZING CASE WITH PERSONALIZATION'")
        print("2. Check if Claude API key is valid (ANTHROPIC_API_KEY)")
        print("3. Check if Pinecone is responding (PINECONE_API_KEY)")
        print("4. Try running: python test_api_connectivity.py")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_analyze()
