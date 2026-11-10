"""Inference task for the study planner (Week 9).

Evidence (what the system knows about the student today):
    Difficulty_A, Difficulty_B, Difficulty_C, PracticeScore, DaysRemaining

Main query, run once per possible action a in {Intense, Light, Rest}:
    Pr(ExamSuccess, Stress | evidence, StudyPlan = a)

The joint over ExamSuccess and Stress is what the utility function (Week 10)
will need, since utility depends on both passing and stress.

Diagnostic query (upstream inference), used to explain the decision:
    Pr(Mastery | evidence)
"""
from src.model import STATES, build_model  # imported first so its warning filter applies

from pgmpy.inference import VariableElimination

EVIDENCE_VARS = ["Difficulty_A", "Difficulty_B", "Difficulty_C", "PracticeScore", "DaysRemaining"]


class Planner:
    def __init__(self):
        self.model = build_model()
        self.infer = VariableElimination(self.model)

    def outcome_given_action(self, evidence, action):
        """Joint Pr(ExamSuccess, Stress | evidence, StudyPlan=action) as a dict
        {(exam, stress): prob}."""
        ev = dict(evidence)
        ev["StudyPlan"] = action
        factor = self.infer.query(["ExamSuccess", "Stress"], evidence=ev,
                                  joint=True, show_progress=False)
        result = {}
        for exam in STATES["ExamSuccess"]:
            for stress in STATES["Stress"]:
                result[(exam, stress)] = float(
                    factor.get_value(ExamSuccess=exam, Stress=stress))
        return result

    def outcomes_all_actions(self, evidence):
        return {a: self.outcome_given_action(evidence, a) for a in STATES["StudyPlan"]}

    def mastery(self, evidence):
        """Pr(Mastery | evidence) as a dict."""
        factor = self.infer.query(["Mastery"], evidence=evidence, show_progress=False)
        return {m: float(factor.get_value(Mastery=m)) for m in STATES["Mastery"]}


def marginal(joint, var):
    """Sum a {(exam, stress): p} table down to one variable."""
    idx = 0 if var == "ExamSuccess" else 1
    out = {}
    for key, p in joint.items():
        out[key[idx]] = out.get(key[idx], 0.0) + p
    return out
