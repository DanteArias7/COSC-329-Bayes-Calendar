"""Draw the draft network to docs/network_draft.png."""
import os
import sys

import matplotlib.pyplot as plt
import networkx as nx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.model import EDGES

# hand placed so it reads top to bottom
POS = {
    "Difficulty_A": (0, 3), "Difficulty_B": (1.5, 3), "Difficulty_C": (3, 3),
    "Mastery": (1.5, 2), "PracticeScore": (0, 1),
    "DaysRemaining": (3.2, 2), "StudyPlan": (4.8, 1),
    "Stress": (3.2, 1), "ExamSuccess": (2.2, 0),
}
OBSERVED = {"Difficulty_A", "Difficulty_B", "Difficulty_C", "PracticeScore", "DaysRemaining"}
DECISION = {"StudyPlan"}

G = nx.DiGraph(EDGES)
colors = []
for n in G.nodes():
    if n in DECISION:
        colors.append("#f6c177")
    elif n in OBSERVED:
        colors.append("#cfe3f5")
    else:
        colors.append("#ffffff")

plt.figure(figsize=(10, 6))
nx.draw_networkx_nodes(G, POS, node_color=colors, edgecolors="black",
                       node_size=4200, node_shape="o")
nx.draw_networkx_labels(G, POS, font_size=7.5)
nx.draw_networkx_edges(G, POS, arrows=True, arrowsize=15, node_size=4200)
plt.title("Draft Bayes net (blue = observed, orange = decision, white = hidden)")
plt.axis("off")
plt.tight_layout()

out = os.path.join(ROOT, "docs", "network_draft.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=150)
print("Saved", out)
