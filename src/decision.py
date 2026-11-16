"""Decision making for the study planner (Week 10).

For each action a:
    EU(a) = sum over exam, stress of  Pr(exam, stress | evidence, StudyPlan=a) * U(exam, stress)
Then pick the action with the highest expected utility.
"""
from src.inference import Planner
from src.model import STATES

# The 3 actions the system can take today. Calendar details are used in Week 11.
ACTIONS = {
    "Intense": {"title": "Intense study block", "hours": 5,
                "description": "Mandatory 5 hour study session"},
    "Light":   {"title": "Light review", "hours": 1,
                "description": "1 hour review of the material"},
    "Rest":    {"title": "Rest day", "hours": 0,
                "description": "Clear the calendar and take a break"},
}

# Utility of each outcome. Passing is worth 100, failing 0,
# and stress takes points away.
EXAM_UTILITY = {"Pass": 100, "Fail": 0}
STRESS_COST = {"Low": 0, "Medium": 15, "High": 40}


def utility(exam, stress, exam_utility=EXAM_UTILITY, stress_cost=STRESS_COST):
    """U(ExamSuccess, Stress)."""
    return exam_utility[exam] - stress_cost[stress]


def utility_table(exam_utility=EXAM_UTILITY, stress_cost=STRESS_COST):
    return {(e, s): utility(e, s, exam_utility, stress_cost)
            for e in STATES["ExamSuccess"] for s in STATES["Stress"]}


def expected_utility(joint, exam_utility=EXAM_UTILITY, stress_cost=STRESS_COST):
    """EU of one action given its joint Pr(ExamSuccess, Stress) table."""
    return sum(p * utility(exam, stress, exam_utility, stress_cost)
               for (exam, stress), p in joint.items())


class DecisionMaker:
    def __init__(self, planner=None):
        self.planner = planner or Planner()

    def decide(self, evidence, exam_utility=EXAM_UTILITY, stress_cost=STRESS_COST):
        """Return a dict with the best action, EU of every action, the
        outcome distributions and the inferred mastery."""
        outcomes = self.planner.outcomes_all_actions(evidence)
        eus = {a: expected_utility(joint, exam_utility, stress_cost)
               for a, joint in outcomes.items()}
        best = max(eus, key=eus.get)
        return {
            "best_action": best,
            "expected_utility": eus,
            "outcomes": outcomes,
            "mastery": self.planner.mastery(evidence),
        }
