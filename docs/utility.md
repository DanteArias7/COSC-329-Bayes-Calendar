# Actions, Utility Function and Expected Utility (Week 10)

## Actions

The system picks one of three actions for today:

| Action | What it does on the calendar |
|---|---|
| **Intense** | Schedules a mandatory 5 hour study block |
| **Light** | Schedules a 1 hour review session |
| **Rest** | Clears the planner's study events for the day |

In the Bayes net the action is the `StudyPlan` node. It affects both `Stress` and `ExamSuccess`, so each action changes the outcome distributions in a different way.

## Utility function

The utility depends on the two query variables, ExamSuccess and Stress:

**U(ExamSuccess, Stress) = U_exam(ExamSuccess) − C_stress(Stress)**

| ExamSuccess | U_exam |
|---|---|
| Pass | 100 |
| Fail | 0 |

| Stress | C_stress |
|---|---|
| Low | 0 |
| Medium | 15 |
| High | 40 |

Full utility table:

| | Stress = Low | Stress = Medium | Stress = High |
|---|---|---|---|
| **Pass** | 100 | 85 | 60 |
| **Fail** | 0 | −15 | −40 |

Reasoning:

- **Exam success matters most.** Passing is worth 100, so even high stress (−40) can't outweigh the difference between passing and failing on its own. This keeps the system focused on the exam.
- **Stress matters too.** Last-minute cramming stress is something the project is supposed to minimize, so it has a real cost.
- **High stress costs much more than medium.** Some stress before an exam is normal, so medium stress is only a small cost. High stress is what leads to burnout, so its cost is more than twice as big.
- **Additive.** The stress cost is the same whether the student passes or fails. This keeps the function simple and easy to explain.

## Expected utility

For each action *a*, the system runs the Week 9 inference query and computes:

**EU(a) = Σ over exam, stress of Pr(exam, stress | evidence, StudyPlan = a) · U(exam, stress)**

where evidence = Difficulty_A, Difficulty_B, Difficulty_C, PracticeScore, DaysRemaining. It then takes the action with the **highest EU**.

Because the utility is additive, this works out to:

EU(a) = 100 · P(Pass | a) − 15 · P(Stress = Medium | a) − 40 · P(Stress = High | a)

### Worked example: struggling student, exam in a few days

From the inference results:

| Action | P(Pass) | P(Stress = Medium) | P(Stress = High) |
|---|---|---|---|
| Intense | 0.514 | 0.217 | 0.727 |
| Light | 0.438 | 0.317 | 0.591 |
| Rest | 0.317 | 0.408 | 0.424 |

- EU(Intense) = 100(0.514) − 15(0.217) − 40(0.727) = 51.4 − 3.3 − 29.1 = **19.1**
- EU(Light) = 100(0.438) − 15(0.317) − 40(0.591) = 43.8 − 4.8 − 23.6 = **15.4**
- EU(Rest) = 100(0.317) − 15(0.408) − 40(0.424) = 31.7 − 6.1 − 17.0 = **8.7**

Intense has the highest EU, so the system schedules the 5 hour block. The extra stress is worth it because studying raises this student's chance of passing by almost 20 points.

## Results

Full tables are in [week10_decision_results.md](week10_decision_results.md).

| Student | Best action | EU (Intense / Light / Rest) |
|---|---|---|
| Struggling, exam soon | **Intense** | 19.1 / 15.4 / 8.7 |
| Struggling, lots of time | **Intense** | 31.9 / 30.3 / 24.9 |
| Average, exam soon | **Light** | 39.8 / 41.8 / 39.7 |
| Average, about a week left | **Light** | 46.8 / 49.4 / 48.0 |
| Advanced, exam soon | **Rest** | 57.3 / 62.9 / 67.0 |
| Advanced, lots of time | **Rest** | 74.5 / 79.1 / 79.4 |

- **Struggling students get the intense block.** They have the most to gain from studying, so the higher chance of passing outweighs the stress.
- **Average students get a light review.** It gets most of the benefit of studying without the high stress of a 5 hour block.
- **Advanced students get a rest day.** Studying barely changes their chance of passing (80.0% → 82.0%), so it isn't worth the stress, especially right before the exam.

Some margins are small, like 79.1 vs 79.4 for the advanced student with lots of time. That makes sense: when a student is in good shape, a light review and a rest day really are about equally good.

## Sensitivity to the utility weights

To check that the results aren't just a result of the exact numbers chosen, I reran the decision with different stress costs ([utility_sensitivity.md](utility_sensitivity.md)):

| Stress cost (Medium, High) | Struggling, soon | Struggling, lots of time | Average, soon | Average, week left | Advanced, soon | Advanced, lots of time |
|---|---|---|---|---|---|---|
| (0, 0) | Intense | Intense | Intense | Intense | Light | Light |
| (10, 30) | Intense | Intense | Light | Light | Rest | Light |
| **(15, 40)** | **Intense** | **Intense** | **Light** | **Light** | **Rest** | **Rest** |
| (20, 50) | Intense | Intense | Light | Rest | Rest | Rest |
| (30, 80) | Light | Rest | Rest | Rest | Rest | Rest |

- If stress has no cost, the system almost always says to study hard, which is what a pure "maximize grades" planner would do.
- As stress costs more, the system moves toward rest, starting with the strongest students and moving down to the weakest.
- The ordering never flips. A struggling student always gets at least as much studying as an advanced one, for every setting.

So the utility weights control how much the system cares about stress, and (15, 40) sits in the middle, where all three actions get used.

## Change to a Week 9 CPT

With the original Week 9 numbers, **Light was almost never the best action** for any weights I tried. Its boost to P(Pass) was set to exactly the middle between Intense and Rest, so one of the two extremes always had a higher EU.

I raised the Light boost in Pr(ExamSuccess | Mastery, StudyPlan, Stress) from (+0.10, +0.07, +0.03) to **(+0.15, +0.10, +0.04)** for Low/Medium/High mastery. The reasoning: one hour of review gets you more than a fifth of the benefit of five hours, because the first hour covers the most important material (diminishing returns per hour). This is more realistic and lets the system recommend a light session when that's the sensible middle ground. [cpts.md](cpts.md) and the full CPT tables have been updated to match.
