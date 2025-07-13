"""Convert Apple Health export to SMASH format using native Python libraries"""

import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def process_health_export(zip_path: Path) -> Dict[str, Any]:
    """Main function to process Apple Health export zip"""

    # Extract and parse the XML
    with zipfile.ZipFile(zip_path, "r") as zf:
        # Find export.xml in the zip (might be in a subdirectory)
        xml_filename = None
        for filename in zf.namelist():
            if filename.endswith("export.xml"):
                xml_filename = filename
                break

        if not xml_filename:
            raise ValueError("No export.xml found in the zip file")

        with zf.open(xml_filename) as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()

    # Extract records into pandas DataFrame
    records = []
    for record in root.findall(".//Record"):
        records.append(
            {
                "type": record.get("type"),
                "sourceName": record.get("sourceName"),
                "unit": record.get("unit"),
                "creationDate": record.get("creationDate"),
                "startDate": record.get("startDate"),
                "endDate": record.get("endDate"),
                "value": record.get("value"),
            }
        )

    df_records = pd.DataFrame(records)

    # Convert dates to datetime (timezone-naive for easier comparison)
    if not df_records.empty:
        df_records["startDate"] = pd.to_datetime(
            df_records["startDate"]
        ).dt.tz_localize(None)
        df_records["endDate"] = pd.to_datetime(df_records["endDate"]).dt.tz_localize(
            None
        )
        df_records["value"] = pd.to_numeric(df_records["value"], errors="coerce")

    # Extract workouts
    workouts = []
    for workout in root.findall(".//Workout"):
        workouts.append(
            {
                "workoutActivityType": workout.get("workoutActivityType"),
                "duration": float(workout.get("duration", 0)),
                "startDate": workout.get("startDate"),
                "endDate": workout.get("endDate"),
                "sourceName": workout.get("sourceName"),
            }
        )

    df_workouts = pd.DataFrame(workouts)
    if not df_workouts.empty:
        df_workouts["startDate"] = pd.to_datetime(
            df_workouts["startDate"]
        ).dt.tz_localize(None)
        df_workouts["endDate"] = pd.to_datetime(df_workouts["endDate"]).dt.tz_localize(
            None
        )

    # Process the data
    measurements = extract_measurements(df_records)
    exercise_data = analyze_workouts(df_workouts)
    sleep_data = analyze_sleep(df_records)

    # Build SMASH format
    smash = {
        "data_source": "apple_health",
        "social_history": {
            "food": "Not available in HealthKit",
            "exercise": exercise_data,
            "drugs": "Not available in HealthKit",
            "tobacco": "Not available in HealthKit",
            "alcohol": {"description": "Not available in HealthKit", "rating": 0},
            "sleep": sleep_data,
            "occupation": "Not available in HealthKit",
            "sexual_history": "Not available in HealthKit",
        },
        "medical_history": {
            "conditions": [],
            "immunizations": [],
            "health_maintenance": {},
        },
        "allergies": [],
        "surgical_history": [],
        "hospitalizations": [],
        "family_history": {"mother": [], "father": [], "siblings": []},
        "medications": [],
        "pcp": {
            "name": "Not available in HealthKit",
            "clinic": "",
            "address": "",
            "phone": "",
            "email": "",
            "last_visit": "",
        },
        "forecast": {
            "life_expectancy_years": 0,
            "cardiovascular_event_10yr_probability": 0,
            "energy_level": "Unknown",
            "metabolic_disease_risk": "Unknown",
            "dementia_risk": "Unknown",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        },
        "measurements": measurements,
    }

    return smash


def extract_measurements(df: pd.DataFrame) -> Dict[str, int]:
    """Extract latest measurements from records DataFrame"""
    measurements = {
        "weight": 0,
        "height": 0,
        "blood_pressure": 0,
        "blood_sugar": 0,
        "cholesterol": 0,
        "hdl": 0,
        "ldl": 0,
        "triglycerides": 0,
    }

    if df.empty:
        return measurements

    # Helper function to get latest value for a record type
    def get_latest_value(record_type: str, unit_conversion: float = 1.0) -> int:
        type_df = df[df["type"] == record_type]
        if not type_df.empty:
            latest = type_df.nlargest(1, "startDate").iloc[0]
            return int(latest["value"] * unit_conversion)
        return 0

    # Weight - convert from lb to lb (no conversion needed)
    measurements["weight"] = get_latest_value("HKQuantityTypeIdentifierBodyMass")

    # Height - convert from feet to inches
    measurements["height"] = get_latest_value(
        "HKQuantityTypeIdentifierHeight", 12.0
    )  # 12 inches per foot

    # Blood pressure (systolic)
    measurements["blood_pressure"] = get_latest_value(
        "HKQuantityTypeIdentifierBloodPressureSystolic"
    )

    # Heart rate (resting)
    heart_rate = get_latest_value("HKQuantityTypeIdentifierHeartRate")
    if heart_rate:
        measurements["resting_heart_rate"] = heart_rate

    # Blood glucose
    measurements["blood_sugar"] = get_latest_value(
        "HKQuantityTypeIdentifierBloodGlucose"
    )

    # Cholesterol values
    measurements["cholesterol"] = get_latest_value(
        "HKQuantityTypeIdentifierDietaryCholesterol"
    )

    return measurements


def analyze_workouts(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze workout patterns from the last 30 days"""
    if df.empty:
        return {"description": "No workout data", "rating": 0}

    # Filter last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_workouts = df[df["startDate"] > thirty_days_ago]

    if recent_workouts.empty:
        return {"description": "No recent workout data", "rating": 0}

    # Calculate workout frequency
    workout_count = len(recent_workouts)
    weekly_avg = workout_count / 4.3  # ~4.3 weeks in 30 days

    # Determine rating based on frequency
    if weekly_avg >= 5:
        rating = 9
        frequency = "5+ times/week"
    elif weekly_avg >= 3:
        rating = 8
        frequency = "3-4 times/week"
    elif weekly_avg >= 1:
        rating = 6
        frequency = "1-2 times/week"
    else:
        rating = 3
        frequency = "Less than weekly"

    # Get most common workout type
    if "workoutActivityType" in recent_workouts.columns:
        workout_counts = recent_workouts["workoutActivityType"].value_counts()
        if not workout_counts.empty:
            most_common = workout_counts.index[0]
            workout_type = most_common.replace("HKWorkoutActivityType", "")
            description = f"{workout_type} {frequency}"
        else:
            description = frequency
    else:
        description = frequency

    return {"description": description, "rating": rating}


def analyze_sleep(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze sleep patterns from records"""
    if df.empty:
        return {"description": "No sleep data", "rating": 5}

    # Filter sleep analysis records
    sleep_df = df[df["type"] == "HKCategoryTypeIdentifierSleepAnalysis"]

    if sleep_df.empty:
        return {"description": "No sleep data", "rating": 5}

    # Filter last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_sleep = sleep_df[sleep_df["startDate"] > thirty_days_ago]

    if recent_sleep.empty:
        return {"description": "No recent sleep data", "rating": 5}

    # Calculate sleep duration for each night
    recent_sleep = recent_sleep.copy()
    recent_sleep["duration_hours"] = (
        recent_sleep["endDate"] - recent_sleep["startDate"]
    ).dt.total_seconds() / 3600

    # Group by date and sum sleep duration
    recent_sleep["date"] = recent_sleep["startDate"].dt.date
    daily_sleep = recent_sleep.groupby("date")["duration_hours"].sum()

    # Calculate average
    avg_hours = daily_sleep.mean()

    # Determine rating
    if avg_hours >= 7.5:
        rating = 9
    elif avg_hours >= 6.5:
        rating = 8
    elif avg_hours >= 5.5:
        rating = 6
    else:
        rating = 4

    description = f"{avg_hours:.1f} hours/night"

    return {"description": description, "rating": rating}
