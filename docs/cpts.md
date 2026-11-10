# CPTs and Inference Task (Week 9)

All CPTs are hand-crafted from my own intuition about studying (no data), the same way the KRIT physics tutor's student model was built from expert knowledge. Every row of every table sums to 1.

Mastery, Stress and ExamSuccess each have 3 parents with 3 values, which is 27 rows per table. Writing 27 rows by hand would be error-prone and hard to justify one at a time, so each of these tables is built from a small **scoring rule**. The rule is the hand-crafted part, and it makes the reasoning easy to explain. The full generated tables are in [cpt_tables.md](cpt_tables.md).

## Priors

| Variable | Prior | Reasoning |
|---|---|---|
| Difficulty_A/B/C | Easy 0.3, Medium 0.4, Hard 0.3 | Most concepts are medium. These are always observed when the system runs, so the prior rarely matters. |
| DaysRemaining | Few 0.3, Some 0.4, Many 0.3 | Also always observed (calculated from the exam date on the calendar). |
| StudyPlan | 1/3 each | This is the decision variable. It's always set as evidence, so it gets a uniform prior (no preference before computing utilities). |

## Pr(Mastery | Difficulty_A, Difficulty_B, Difficulty_C)

Each concept adds difficulty points: **Easy = 0, Medium = 1, Hard = 2**. The total (0 to 6) sets the Mastery distribution:

| Difficulty points | Low | Medium | High |
|---|---|---|---|
| 0 (all easy) | 0.05 | 0.25 | 0.70 |
| 1 | 0.10 | 0.30 | 0.60 |
| 2 | 0.15 | 0.40 | 0.45 |
| 3 | 0.25 | 0.45 | 0.30 |
| 4 | 0.40 | 0.40 | 0.20 |
| 5 | 0.55 | 0.35 | 0.10 |
| 6 (all hard) | 0.70 | 0.25 | 0.05 |

- The harder the material is for the student, the less likely they've mastered it.
- No row goes to 0. Even if every concept is hard, a student could still have high mastery (e.g. they've studied a lot), just unlikely.
- Treating the three concepts equally assumes they're weighted the same on the exam. Weights could be added later.

## Pr(PracticeScore | Mastery)

| Mastery | Low | Medium | High |
|---|---|---|---|
| Low | 0.70 | 0.25 | 0.05 |
| Medium | 0.20 | 0.60 | 0.20 |
| High | 0.05 | 0.25 | 0.70 |

- Strong diagonal: a student's practice scores usually match how well they know the material, like Pr(NumericallyCorrect | Algebra) in the KRIT reading.
- Off-diagonal values cover bad days, lucky guesses, or a practice quiz that didn't match the exam.
- This is the observation that lets the system do **upstream inference** on Mastery, which is hidden.

## Pr(Stress | DaysRemaining, Mastery, StudyPlan)

Stress points from each parent:

| Parent | Values → points |
|---|---|
| DaysRemaining | Few = 2, Some = 1, Many = 0 |
| Mastery | Low = 2, Medium = 1, High = 0 |
| StudyPlan | Intense = +1, Light = 0, Rest = −1 |

The total (−1 to 5) sets the Stress distribution:

| Stress points | Low | Medium | High |
|---|---|---|---|
| −1 | 0.80 | 0.15 | 0.05 |
| 0 | 0.65 | 0.25 | 0.10 |
| 1 | 0.45 | 0.40 | 0.15 |
| 2 | 0.25 | 0.45 | 0.30 |
| 3 | 0.15 | 0.40 | 0.45 |
| 4 | 0.08 | 0.30 | 0.62 |
| 5 | 0.05 | 0.20 | 0.75 |

- An exam coming up soon is the biggest source of stress (last-minute cramming).
- Feeling unprepared (low mastery) adds as much stress as being short on time.
- A 5-hour intense block adds stress, and a rest day takes some away. A light review doesn't change it.
- Example: exam in 2 days (2) + low mastery (2) + intense block (1) = 5 points → 75% chance of high stress.

## Pr(ExamSuccess | Mastery, StudyPlan, Stress)

**P(Pass) = base from Mastery + boost from StudyPlan − penalty from Stress**, clipped to [0.02, 0.98].

| Mastery | Base P(Pass) | Intense boost | Light boost | Rest boost |
|---|---|---|---|---|
| Low | 0.35 | +0.25 | +0.10 | 0 |
| Medium | 0.65 | +0.15 | +0.07 | 0 |
| High | 0.88 | +0.05 | +0.03 | 0 |

| Stress | Penalty |
|---|---|
| Low | 0 |
| Medium | −0.05 |
| High | −0.15 |

- Mastery is the main factor in passing.
- Studying helps weaker students a lot more than students who already know the material (diminishing returns). This is what lets the system tell a struggling student from an advanced one.
- High stress hurts exam performance, so an intense block isn't free: it raises the chance of passing but also raises stress, which partly cancels the gain.
- P(Pass) never hits exactly 0 or 1, because nothing is certain on exam day.
- P(Fail) = 1 − P(Pass).

## Inference task

**Evidence** (known about the student each day): Difficulty_A, Difficulty_B, Difficulty_C, PracticeScore, DaysRemaining.

**Main query**, run once for each possible action *a* ∈ {Intense, Light, Rest}:

> Pr(ExamSuccess, Stress | Difficulty_A, Difficulty_B, Difficulty_C, PracticeScore, DaysRemaining, StudyPlan = *a*)

Mastery is hidden and gets summed out. The query returns the **joint** over ExamSuccess and Stress, because the utility function (Week 10) depends on both. Comparing the three results shows how each action trades exam success against stress.

**Diagnostic query** (upstream inference), used to explain the decision to the student:

> Pr(Mastery | Difficulty_A, Difficulty_B, Difficulty_C, PracticeScore)

**Algorithm:** pgmpy's built-in Variable Elimination (`pgmpy.inference.VariableElimination`). The network is small (9 variables, largest table 81 entries), so exact inference is fast.

## Test results

Test queries on four example students are in [week9_inference_results.md](week9_inference_results.md). The main things they show:

- **Struggling student, exam soon:** an intense block raises P(Pass) from 31.7% (rest) to 51.4%, but P(high stress) goes from 42% to 73%.
- **Advanced student, exam soon:** an intense block only raises P(Pass) from 80.0% to 82.0%, while P(high stress) goes from 17% to 47%. Studying hard barely helps but costs a lot of stress.
- **Same struggling student with lots of time:** stress is much lower for every action, so the intense block costs less.

So the model gives the utility function a real tradeoff to work with, and different students should end up with different best actions in Week 10.
