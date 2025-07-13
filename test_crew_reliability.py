#!/usr/bin/env python3
"""Test the /visit-crew endpoint reliability by running it multiple times."""

import json
import time

import requests

# Test configuration
API_URL = "http://localhost:8000/visit-crew"
NUM_TESTS = 10  # Reduced for quicker testing
TIMEOUT = 65  # seconds (slightly more than the 60s timeout in the API)

# Test data
TEST_PATIENT_DATA = {
    "social_history": {
        "food": "Mediterranean diet with occasional processed foods",
        "exercise": {"description": "Walks 30 minutes 3x/week", "rating": 6},
        "drugs": "None",
        "tobacco": "Never smoker",
        "alcohol": {"description": "2-3 glasses of wine per week", "rating": 7},
        "sleep": {
            "description": "6-7 hours per night, occasional insomnia",
            "rating": 6,
        },
        "occupation": "Software engineer - sedentary",
        "sexual_history": "Not relevant",
    },
    "medical_history": {
        "conditions": ["Hypertension", "Pre-diabetes"],
        "immunizations": ["COVID-19", "Flu 2023"],
        "health_maintenance": {},
    },
    "allergies": [{"allergen": "Penicillin", "reaction": "Rash"}],
    "surgical_history": ["Appendectomy 2015"],
    "hospitalizations": [],
    "family_history": {
        "father": ["Diabetes Type 2", "Heart Disease"],
        "mother": ["Osteoporosis"],
        "siblings": [],
    },
    "medications": [
        {"name": "Lisinopril", "dose": "10mg daily"},
        {"name": "Metformin", "dose": "500mg twice daily"},
    ],
    "pcp": {
        "name": "Dr. Smith",
        "clinic": "Primary Care Associates",
        "address": "123 Main St",
        "phone": "555-0100",
        "email": "dr.smith@example.com",
        "last_visit": "2024-01-15",
    },
    "forecast": {
        "life_expectancy_years": 82.5,
        "cardiovascular_event_10yr_probability": 0.15,
        "energy_level": "Moderate",
        "metabolic_disease_risk": "High",
        "dementia_risk": "Low",
    },
    "measurements": {
        "weight": 185,
        "height": 70,
        "blood_pressure": "135/85",
        "blood_sugar": 110,
        "cholesterol": 210,
        "hdl": 45,
        "ldl": 140,
        "triglycerides": 150,
    },
}


def validate_response(response_data):
    """Validate that the response has all required fields."""
    # Check for recommendations
    if "recommendations" not in response_data:
        return False, "Missing recommendations"

    recs = response_data["recommendations"]
    required_recs = ["alcohol", "sleep", "exercise", "supplements"]
    for rec in required_recs:
        if rec not in recs:
            return False, f"Missing recommendation: {rec}"

    # Check that supplements is a list with at least one item
    if not isinstance(recs["supplements"], list) or len(recs["supplements"]) == 0:
        return False, "Supplements should be a non-empty list"

    # Check for forecast
    if "forecast" not in response_data:
        return False, "Missing forecast"

    return True, "Valid response"


def run_single_test(test_num):
    """Run a single test and return success status and details."""
    print(f"\nTest {test_num}: ", end="", flush=True)
    start_time = time.time()

    try:
        response = requests.post(
            API_URL,
            json=TEST_PATIENT_DATA,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            try:
                data = response.json()
                is_valid, message = validate_response(data)
                if is_valid:
                    print(f"✓ PASSED ({elapsed_time:.1f}s)")
                    return True, elapsed_time, "Success"
                else:
                    print(
                        f"✗ FAILED - Invalid response: {message} ({elapsed_time:.1f}s)"
                    )
                    return False, elapsed_time, f"Invalid response: {message}"
            except json.JSONDecodeError:
                print(f"✗ FAILED - Invalid JSON ({elapsed_time:.1f}s)")
                return False, elapsed_time, "Invalid JSON response"
        else:
            print(
                f"✗ FAILED - HTTP {response.status_code}: {response.text[:100]} ({elapsed_time:.1f}s)"
            )
            return False, elapsed_time, f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"✗ FAILED - Timeout after {elapsed_time:.1f}s")
        return False, elapsed_time, "Timeout"
    except requests.exceptions.RequestException as e:
        elapsed_time = time.time() - start_time
        print(f"✗ FAILED - Request error: {str(e)} ({elapsed_time:.1f}s)")
        return False, elapsed_time, f"Request error: {str(e)}"


def main():
    """Run multiple tests and report results."""
    print(f"Testing {API_URL} with {NUM_TESTS} sequential requests...")
    print(f"Timeout: {TIMEOUT}s per request")
    print("=" * 60)

    results = []
    total_time = 0

    for i in range(1, NUM_TESTS + 1):
        success, elapsed_time, details = run_single_test(i)
        results.append({"success": success, "time": elapsed_time, "details": details})
        total_time += elapsed_time

        # Small delay between tests to avoid overwhelming the server
        if i < NUM_TESTS:
            time.sleep(1)

    # Calculate statistics
    successes = sum(1 for r in results if r["success"])
    failures = NUM_TESTS - successes
    success_rate = (successes / NUM_TESTS) * 100

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Total tests: {NUM_TESTS}")
    print(f"  Passed: {successes}")
    print(f"  Failed: {failures}")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Average time per test: {total_time / NUM_TESTS:.1f}s")

    if failures > 0:
        print("\nFailure details:")
        for i, result in enumerate(results):
            if not result["success"]:
                print(f"  Test {i + 1}: {result['details']}")


if __name__ == "__main__":
    main()

