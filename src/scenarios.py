"""Simulated student types (Week 11).

Each profile fixes how hard the three concepts are for the student and how
they're doing on practice questions. DaysRemaining is not part of the
profile: it's worked out each day from the exam date.
"""

STUDENT_PROFILES = {
    "struggling": {
        "label": "Struggling student",
        "evidence": {"Difficulty_A": "Hard", "Difficulty_B": "Hard", "Difficulty_C": "Medium",
                     "PracticeScore": "Low"},
    },
    "average": {
        "label": "Average student",
        "evidence": {"Difficulty_A": "Medium", "Difficulty_B": "Medium", "Difficulty_C": "Medium",
                     "PracticeScore": "Medium"},
    },
    "advanced": {
        "label": "Advanced student",
        "evidence": {"Difficulty_A": "Easy", "Difficulty_B": "Easy", "Difficulty_C": "Medium",
                     "PracticeScore": "High"},
    },
}
