"""Week 10: check how much the chosen actions depend on the stress costs in
the utility function. Writes docs/utility_sensitivity.md.

Run from the project root:
    python scripts/sensitivity.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scripts.run_decision import STUDENTS
from src.decision import EXAM_UTILITY, DecisionMaker

# (medium stress cost, high stress cost) pairs to try. (15, 40) is the one used.
SETTINGS = [(0, 0), (5, 20), (10, 30), (15, 40), (20, 50), (25, 60), (30, 80)]


def main():
    dm = DecisionMaker()
    short = {name: name.replace("student, ", "") for name in STUDENTS}
    header = "| Stress cost (Medium, High) | " + " | ".join(short.values()) + " |"
    lines = ["# Utility Sensitivity Check", "",
             "Best action for each student as the stress costs change. Pass = 100, Fail = 0 throughout.",
             "The row in bold is the utility function used by the system.", "",
             header, "|" + "---|" * (len(STUDENTS) + 1)]

    for med, high in SETTINGS:
        cost = {"Low": 0, "Medium": med, "High": high}
        picks = [dm.decide(ev, EXAM_UTILITY, cost)["best_action"] for ev in STUDENTS.values()]
        label = f"({med}, {high})"
        if (med, high) == (15, 40):
            label = f"**{label}**"
            picks = [f"**{p}**" for p in picks]
        lines.append(f"| {label} | " + " | ".join(picks) + " |")

    text = "\n".join(lines)
    print(text)
    out = os.path.join(ROOT, "docs", "utility_sensitivity.md")
    with open(out, "w") as f:
        f.write(text + "\n")
    print("Saved", out)


if __name__ == "__main__":
    main()
