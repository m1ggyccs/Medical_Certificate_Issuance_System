from datetime import datetime
from expert_system import analyze_case

# Demo cases
cases = [
    {
        "student_id": "S0001",
        "has_excuse_letter": True,
        "valid_id": True,
        "symptoms": ["cough", "fever"],
        "illness_type": "simple",
        "timestamp": datetime.now()
    },
    {
        "student_id": "S0002",
        "has_excuse_letter": False,
        "valid_id": True,
        "symptoms": ["headache"],
        "illness_type": "simple",
        "timestamp": datetime.now()
    },
    {
        "student_id": "S0003",
        "has_excuse_letter": True,
        "valid_id": True,
        "symptoms": ["recurring fever", "chronic pain"],
        "illness_type": "complex",
        "timestamp": datetime.now()
    },
    {
        "student_id": "S0004",
        "has_excuse_letter": True,
        "valid_id": False,
        "symptoms": ["flu"],
        "illness_type": "simple",
        "timestamp": datetime.now()
    },
    {
        "student_id": "S0005",
        "has_excuse_letter": True,
        "valid_id": True,
        "symptoms": ["mental health issues", "severe injury"],
        "illness_type": "complex",
        "timestamp": datetime.now()
    }
]

print("=== Expert System Demo ===\n")
for i, case in enumerate(cases, 1):
    result = analyze_case(case)
    print(f"Case {i}:")
    print(f"  Input: {case}")
    print(f"  Output: {result}\n")