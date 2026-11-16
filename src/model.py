"""Bayes net for the study planner.

Week 8: variables and structure.
Week 9: hand-crafted CPTs. The reasoning for every number is in docs/cpts.md.

The three big CPTs (Mastery, Stress, ExamSuccess) each have 27 parent
combinations, so instead of typing every row by hand they are built from
simple scoring rules. The rules are the hand-crafted part.
"""
import warnings
from itertools import product

warnings.filterwarnings("ignore", category=FutureWarning)  # noisy pgmpy deprecation warning

from pgmpy.factors.discrete import TabularCPD
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

PARENTS = {
    "Mastery": ["Difficulty_A", "Difficulty_B", "Difficulty_C"],
    "PracticeScore": ["Mastery"],
    "Stress": ["DaysRemaining", "Mastery", "StudyPlan"],
    "ExamSuccess": ["Mastery", "StudyPlan", "Stress"],
}

# ---------------------------------------------------------------------------
# Priors (root nodes)
# ---------------------------------------------------------------------------
# Difficulty and DaysRemaining are always observed when the system runs, so
# these priors only matter if a query leaves them out.
PRIORS = {
    "Difficulty_A": [0.3, 0.4, 0.3],   # Easy, Medium, Hard
    "Difficulty_B": [0.3, 0.4, 0.3],
    "Difficulty_C": [0.3, 0.4, 0.3],
    "DaysRemaining": [0.3, 0.4, 0.3],  # Few, Some, Many
    # StudyPlan is the decision. It is always set as evidence, so it gets a
    # uniform prior (the system has no preference before it computes utilities).
    "StudyPlan": [1 / 3, 1 / 3, 1 / 3],  # Intense, Light, Rest
}

# ---------------------------------------------------------------------------
# Pr(Mastery | Difficulty_A, Difficulty_B, Difficulty_C)
# ---------------------------------------------------------------------------
# Each concept adds difficulty points: Easy = 0, Medium = 1, Hard = 2.
# Total goes from 0 (all easy) to 6 (all hard). More points -> lower mastery.
DIFFICULTY_POINTS = {"Easy": 0, "Medium": 1, "Hard": 2}
MASTERY_BY_DIFFICULTY = {
    #     Low   Medium High
    0: [0.05, 0.25, 0.70],
    1: [0.10, 0.30, 0.60],
    2: [0.15, 0.40, 0.45],
    3: [0.25, 0.45, 0.30],
    4: [0.40, 0.40, 0.20],
    5: [0.55, 0.35, 0.10],
    6: [0.70, 0.25, 0.05],
}

# ---------------------------------------------------------------------------
# Pr(PracticeScore | Mastery)  -- rows: Mastery, columns: Low, Medium, High
# ---------------------------------------------------------------------------
PRACTICE_GIVEN_MASTERY = {
    "Low":    [0.70, 0.25, 0.05],
    "Medium": [0.20, 0.60, 0.20],
    "High":   [0.05, 0.25, 0.70],
}

# ---------------------------------------------------------------------------
# Pr(Stress | DaysRemaining, Mastery, StudyPlan)
# ---------------------------------------------------------------------------
# Stress points: less time, lower mastery and a heavier plan all add stress.
STRESS_POINTS = {
    "DaysRemaining": {"Few": 2, "Some": 1, "Many": 0},
    "Mastery": {"Low": 2, "Medium": 1, "High": 0},
    "StudyPlan": {"Intense": 1, "Light": 0, "Rest": -1},
}
STRESS_BY_POINTS = {
    #      Low   Medium High
    -1: [0.80, 0.15, 0.05],
    0: [0.65, 0.25, 0.10],
    1: [0.45, 0.40, 0.15],
    2: [0.25, 0.45, 0.30],
    3: [0.15, 0.40, 0.45],
    4: [0.08, 0.30, 0.62],
    5: [0.05, 0.20, 0.75],
}

# ---------------------------------------------------------------------------
# Pr(ExamSuccess | Mastery, StudyPlan, Stress)
# ---------------------------------------------------------------------------
# P(Pass) = base chance from Mastery + boost from today's plan - stress penalty
PASS_BASE = {"Low": 0.35, "Medium": 0.65, "High": 0.88}
# studying helps weaker students more than students who already know it.
# Week 10: Light boost raised from (0.10, 0.07, 0.03). A 1 hour review gets you
# more than 1/5 of the benefit of a 5 hour block (diminishing returns per hour),
# and with the old values Light was never the best action. See docs/utility.md.
PLAN_BOOST = {
    "Intense": {"Low": 0.25, "Medium": 0.15, "High": 0.05},
    "Light":   {"Low": 0.15, "Medium": 0.10, "High": 0.04},
    "Rest":    {"Low": 0.00, "Medium": 0.00, "High": 0.00},
}
STRESS_PENALTY = {"Low": 0.00, "Medium": 0.05, "High": 0.15}


def _columns(parents):
    """All parent value combinations in the order pgmpy expects
    (last parent changes fastest)."""
    return list(product(*[STATES[p] for p in parents]))


def mastery_dist(a, b, c):
    points = DIFFICULTY_POINTS[a] + DIFFICULTY_POINTS[b] + DIFFICULTY_POINTS[c]
    return MASTERY_BY_DIFFICULTY[points]


def stress_dist(days, mastery, plan):
    points = (STRESS_POINTS["DaysRemaining"][days]
              + STRESS_POINTS["Mastery"][mastery]
              + STRESS_POINTS["StudyPlan"][plan])
    return STRESS_BY_POINTS[points]


def pass_prob(mastery, plan, stress):
    p = PASS_BASE[mastery] + PLAN_BOOST[plan][mastery] - STRESS_PENALTY[stress]
    p = min(max(p, 0.02), 0.98)  # never fully certain
    return round(p, 4)


def _make_cpt(variable, parents, dist_fn):
    cols = _columns(parents)
    dists = [dist_fn(*combo) for combo in cols]
    # pgmpy wants one row per value of the variable, one column per parent combo
    values = [[d[i] for d in dists] for i in range(len(STATES[variable]))]
    return TabularCPD(
        variable, len(STATES[variable]), values,
        evidence=parents,
        evidence_card=[len(STATES[p]) for p in parents],
        state_names={variable: STATES[variable], **{p: STATES[p] for p in parents}},
    )


def build_cpts():
    cpts = []
    for var, probs in PRIORS.items():
        cpts.append(TabularCPD(var, len(STATES[var]), [[p] for p in probs],
                               state_names={var: STATES[var]}))

    cpts.append(_make_cpt("Mastery", PARENTS["Mastery"], mastery_dist))
    cpts.append(_make_cpt("PracticeScore", PARENTS["PracticeScore"],
                          lambda m: PRACTICE_GIVEN_MASTERY[m]))
    cpts.append(_make_cpt("Stress", PARENTS["Stress"], stress_dist))
    cpts.append(_make_cpt("ExamSuccess", PARENTS["ExamSuccess"],
                          lambda m, p, s: [pass_prob(m, p, s), round(1 - pass_prob(m, p, s), 4)]))
    return cpts


def build_structure():
    """Return the network with nodes and edges only (no CPTs)."""
    return DiscreteBayesianNetwork(EDGES)


def build_model():
    """Return the full network with all CPTs attached and checked."""
    model = DiscreteBayesianNetwork(EDGES)
    model.add_cpds(*build_cpts())
    assert model.check_model()
    return model


if __name__ == "__main__":
    model = build_model()
    print("Model is valid. Nodes:", len(model.nodes()))
    for node in STATES:
        cpd = model.get_cpds(node)
        print(f"  {node:14s} parents={model.get_parents(node)}  table size={cpd.values.size}")
