"""First draft of the Bayes net structure (Week 8).

Only the variables, their values and the edges for now.
CPTs get filled in Week 9. See docs/network_draft.md for the reasoning.
"""
from pgmpy.models import DiscreteBayesianNetwork

# variable -> list of values
STATES = {
    # how hard each concept on the exam is (for this student)
    "Difficulty_A": ["Easy", "Medium", "Hard"],
    "Difficulty_B": ["Easy", "Medium", "Hard"],
    "Difficulty_C": ["Easy", "Medium", "Hard"],
    # hidden: how well the student knows the material overall
    "Mastery": ["Low", "Medium", "High"],
    # observed: recent practice quiz / problem set results
    "PracticeScore": ["Low", "Medium", "High"],
    # observed: days left until the exam (Few = 0-3, Some = 4-7, Many = 8+)
    "DaysRemaining": ["Few", "Some", "Many"],
    # decision: the action the system takes today (set as evidence for each option)
    "StudyPlan": ["Intense", "Light", "Rest"],
    # hidden: how stressed the student will be
    "Stress": ["Low", "Medium", "High"],
    # outcome we care about
    "ExamSuccess": ["Pass", "Fail"],
}

EDGES = [
    # harder concepts -> lower mastery
    ("Difficulty_A", "Mastery"),
    ("Difficulty_B", "Mastery"),
    ("Difficulty_C", "Mastery"),
    # mastery shows up in practice results (lets us do upstream inference)
    ("Mastery", "PracticeScore"),
    # stress depends on time left, how prepared they are, and today's plan
    ("DaysRemaining", "Stress"),
    ("Mastery", "Stress"),
    ("StudyPlan", "Stress"),
    # passing depends on mastery, how much they study, and stress
    ("Mastery", "ExamSuccess"),
    ("StudyPlan", "ExamSuccess"),
    ("Stress", "ExamSuccess"),
]


def build_structure():
    """Return the network with nodes and edges only (no CPTs yet)."""
    model = DiscreteBayesianNetwork(EDGES)
    return model


if __name__ == "__main__":
    model = build_structure()
    print("Nodes:", len(model.nodes()))
    for node in STATES:
        parents = model.get_parents(node)
        print(f"  {node:14s} parents={parents}  values={STATES[node]}")
