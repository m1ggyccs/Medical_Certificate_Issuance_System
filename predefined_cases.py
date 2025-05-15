"""
Predefined cases for the Medical Certificate Issuance Support System.
Each case represents a typical scenario encountered in the clinic.
"""

TYPICAL_CASES = {
    "case_1": {
        "name": "Fever and Flu",
        "description": "Common cold with fever and body aches",
        "symptoms": [
            "fever (38.5°C)",
            "runny nose",
            "sore throat",
            "body aches",
            "fatigue"
        ],
        "severity": "normal",
        "recommended_days": 2,
        "notes": "Typical viral infection case",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter"]
    },
    "case_2": {
        "name": "Severe Migraine",
        "description": "Intense headache with visual disturbances",
        "symptoms": [
            "severe headache",
            "visual aura",
            "nausea",
            "sensitivity to light"
        ],
        "severity": "moderate",
        "recommended_days": 2,
        "notes": "Requires rest in dark, quiet environment",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter"]
    },
    "case_3": {
        "name": "Acute Gastroenteritis",
        "description": "Food poisoning symptoms",
        "symptoms": [
            "vomiting",
            "diarrhea",
            "abdominal pain",
            "mild fever"
        ],
        "severity": "moderate",
        "recommended_days": 3,
        "notes": "Requires hydration and rest",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter"]
    },
    "case_4": {
        "name": "Respiratory Distress",
        "description": "Difficulty breathing with chest pain",
        "symptoms": [
            "difficulty breathing",
            "chest pain",
            "rapid heartbeat",
            "dizziness"
        ],
        "severity": "high",
        "recommended_days": 5,
        "notes": "Immediate medical attention required",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "previous_medical_records"]
    },
    "case_5": {
        "name": "Sports Injury",
        "description": "Ankle sprain during sports activity",
        "symptoms": [
            "ankle pain",
            "swelling",
            "difficulty walking",
            "bruising"
        ],
        "severity": "moderate",
        "recommended_days": 3,
        "notes": "RICE protocol recommended",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter", "incident_report"]
    },
    "case_6": {
        "name": "Mental Health Day",
        "description": "Stress and anxiety symptoms",
        "symptoms": [
            "anxiety",
            "difficulty concentrating",
            "fatigue",
            "sleep disturbance"
        ],
        "severity": "normal",
        "recommended_days": 2,
        "notes": "Counseling referral recommended",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "counselor_note"]
    },
    "case_7": {
        "name": "Viral Infection (COVID-like)",
        "description": "Respiratory infection with fever",
        "symptoms": [
            "high fever",
            "dry cough",
            "fatigue",
            "loss of taste/smell"
        ],
        "severity": "high",
        "recommended_days": 7,
        "notes": "COVID test recommended, isolation required",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "test_results"]
    },
    "case_8": {
        "name": "Chronic Condition Flare-up",
        "description": "Asthma exacerbation",
        "symptoms": [
            "wheezing",
            "shortness of breath",
            "chest tightness",
            "coughing fits"
        ],
        "severity": "high",
        "recommended_days": 4,
        "notes": "Known asthmatic patient",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "medical_history", "action_plan"]
    },
    "case_9": {
        "name": "Post-Surgery Follow-up",
        "description": "Recovery from appendectomy",
        "symptoms": [
            "surgical site pain",
            "limited mobility",
            "fatigue",
            "mild fever"
        ],
        "severity": "high",
        "recommended_days": 10,
        "notes": "Post-operative care required",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "surgical_records", "doctor_note"]
    },
    "case_10": {
        "name": "Infectious Disease",
        "description": "Suspected mumps case",
        "symptoms": [
            "swollen salivary glands",
            "fever",
            "headache",
            "muscle aches"
        ],
        "severity": "high",
        "recommended_days": 14,
        "notes": "Isolation required, contact tracing needed",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "test_results", "health_declaration"]
    },
    "case_11": {
        "name": "Minor Injury",
        "description": "Paper cut with mild infection",
        "symptoms": [
            "localized pain",
            "minor swelling",
            "redness"
        ],
        "severity": "low",
        "recommended_days": 1,
        "notes": "Basic first aid sufficient",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter"]
    },
    "case_12": {
        "name": "Seasonal Allergies",
        "description": "Hay fever symptoms",
        "symptoms": [
            "sneezing",
            "itchy eyes",
            "runny nose",
            "congestion"
        ],
        "severity": "low",
        "recommended_days": 1,
        "notes": "Common during spring",
        "requires_doctor": False,
        "documentation_required": ["excuse_letter"]
    },
    "case_13": {
        "name": "Chronic Fatigue",
        "description": "Ongoing fatigue investigation",
        "symptoms": [
            "persistent fatigue",
            "muscle weakness",
            "difficulty concentrating",
            "sleep problems"
        ],
        "severity": "moderate",
        "recommended_days": 5,
        "notes": "Requires comprehensive evaluation",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "medical_history", "test_results"]
    },
    "case_14": {
        "name": "Laboratory Accident",
        "description": "Chemical splash exposure",
        "symptoms": [
            "eye irritation",
            "skin redness",
            "burning sensation"
        ],
        "severity": "high",
        "recommended_days": 3,
        "notes": "Immediate decontamination required",
        "requires_doctor": True,
        "documentation_required": ["excuse_letter", "incident_report", "lab_safety_report"]
    }
}

SIMULATION_SCENARIOS = {
    "normal_day": {
        "name": "Typical Clinic Day",
        "description": "Regular clinic operation with normal patient flow",
        "parameters": {
            "duration_hours": 8,
            "num_doctors": 2,
            "num_nurses": 3,
            "patient_arrival_rate": 15,  # minutes between arrivals
            "case_distribution": {
                "simple": 0.7,  # 70% simple cases
                "complex": 0.3   # 30% complex cases
            }
        }
    },
    "busy_day": {
        "name": "Peak Season",
        "description": "High patient volume during exam period",
        "parameters": {
            "duration_hours": 8,
            "num_doctors": 3,
            "num_nurses": 4,
            "patient_arrival_rate": 10,
            "case_distribution": {
                "simple": 0.6,  # More complex cases during busy periods
                "complex": 0.4
            }
        }
    },
    "quiet_day": {
        "name": "Holiday Period",
        "description": "Low patient volume during holidays",
        "parameters": {
            "duration_hours": 8,
            "num_doctors": 1,
            "num_nurses": 2,
            "patient_arrival_rate": 30,
            "case_distribution": {
                "simple": 0.8,  # Mostly simple cases during quiet periods
                "complex": 0.2
            }
        }
    },
    "emergency_situation": {
        "name": "Campus Health Emergency",
        "description": "Handling a potential outbreak situation",
        "parameters": {
            "duration_hours": 12,  # Extended hours
            "num_doctors": 4,
            "num_nurses": 6,
            "patient_arrival_rate": 5,  # Very frequent arrivals
            "case_distribution": {
                "simple": 0.3,  # Mostly complex cases
                "complex": 0.7
            }
        }
    }
} 