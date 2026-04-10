"""
grader.py — Advanced reward & metrics engine for Email Sorting OpenEnv v2.0

Reward schema
─────────────
  Base score:
    1.0  exact match
    0.5  urgent ↔ normal  (adjacent legitimate-mail confusion)
    0.0  any confusion involving spam

  Confidence bonus (optional, max +0.1):
    When agent supplies confidence ∈ [0,1]:
      +0.1 × confidence   if prediction is correct
      -0.1 × confidence   if prediction is wrong
    → rewards calibrated confidence; penalises overconfident mistakes

  Final score = clamp(base + bonus, 0.0, 1.0)

Advanced metrics
────────────────
  Confusion matrix, per-class precision/recall/F1,
  macro-F1, weighted-F1, accuracy.
"""

from __future__ import annotations
from models import Action, EmailLabel, Reward, ClassMetrics, ConfusionMatrix, EpisodeMetrics

# ── Adjacency (partial credit) ─────────────────────────────────────────────

PARTIAL_CREDIT_PAIRS: set = {
    frozenset({EmailLabel.URGENT, EmailLabel.NORMAL}),
}


# ── Core per-step grader ───────────────────────────────────────────────────

def grade(action: Action, correct_label: EmailLabel) -> Reward:
    """
    Evaluate one action.  Returns a Reward with base_score, confidence_bonus,
    and final score = clamp(base + bonus, 0, 1).
    """
    predicted = EmailLabel(action.label)
    correct   = EmailLabel(correct_label)

    # Base score
    if predicted == correct:
        base, rationale = 1.0, "Correct classification."
    elif frozenset({predicted, correct}) in PARTIAL_CREDIT_PAIRS:
        base = 0.5
        rationale = (
            f"Partial credit: '{predicted.value}' vs '{correct.value}' — "
            "both are legitimate emails; urgency is ambiguous."
        )
    else:
        base = 0.0
        rationale = (
            f"Incorrect: predicted '{predicted.value}', "
            f"correct is '{correct.value}'."
        )

    # Confidence shaping
    bonus = 0.0
    if action.confidence is not None:
        c = max(0.0, min(1.0, action.confidence))
        bonus = round(0.1 * c * (1 if predicted == correct else -1), 4)
        if bonus != 0.0:
            direction = "+" if bonus > 0 else ""
            rationale += f"  [confidence bonus: {direction}{bonus:.2f}]"

    final = round(max(0.0, min(1.0, base + bonus)), 4)

    return Reward(
        score=final,
        base_score=base,
        confidence_bonus=bonus,
        predicted=predicted,
        correct=correct,
        rationale=rationale,
    )


# ── Batch episode grader ───────────────────────────────────────────────────

def grade_episode(
    predictions: list,
    ground_truths: list,
    difficulties: list | None = None,
    agent_name: str = "agent",
) -> EpisodeMetrics:
    """
    Full evaluation for one episode.

    Parameters
    ----------
    predictions   : list[Action]
    ground_truths : list[EmailLabel]
    difficulties  : optional list[str] — per-email difficulty tag
    agent_name    : str label for the leaderboard

    Returns
    -------
    EpisodeMetrics with accuracy, macro/weighted F1, per-class metrics,
    confusion matrix, and per-difficulty average scores.
    """
    if len(predictions) != len(ground_truths):
        raise ValueError("predictions and ground_truths must have the same length.")

    rewards = [grade(a, c) for a, c in zip(predictions, ground_truths)]
    scores  = [r.score for r in rewards]
    n       = len(scores)

    correct   = sum(1 for r in rewards if r.base_score == 1.0)
    partial   = sum(1 for r in rewards if r.base_score == 0.5)
    incorrect = sum(1 for r in rewards if r.base_score == 0.0)

    avg_score = sum(scores) / n
    accuracy  = correct / n

    # Confusion matrix
    pred_vals  = [EmailLabel(a.label) for a in predictions]
    true_vals  = [EmailLabel(c)        for c in ground_truths]
    cm         = ConfusionMatrix.build(pred_vals, true_vals)

    # Per-class precision / recall / F1
    labels     = [e for e in EmailLabel]
    per_class  = []
    f1_scores  = []
    for lbl in labels:
        tp = cm.matrix[lbl.value][lbl.value]
        fp = sum(cm.matrix[other.value][lbl.value] for other in labels if other != lbl)
        fn = sum(cm.matrix[lbl.value][other.value] for other in labels if other != lbl)
        support = tp + fn

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1   = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        per_class.append(ClassMetrics(
            label=lbl.value, precision=round(prec,4),
            recall=round(rec,4), f1=round(f1,4), support=support,
        ))
        f1_scores.append((f1, support))

    macro_f1    = round(sum(f for f, _ in f1_scores) / len(f1_scores), 4)
    total_sup   = sum(s for _, s in f1_scores)
    weighted_f1 = round(
        sum(f * s for f, s in f1_scores) / total_sup if total_sup > 0 else 0.0, 4
    )

    # Per-difficulty breakdown
    per_diff: dict = {}
    if difficulties:
        from collections import defaultdict
        diff_scores: dict = defaultdict(list)
        for sc, diff in zip(scores, difficulties):
            if diff:
                diff_scores[diff].append(sc)
        per_diff = {
            d: round(sum(v)/len(v), 4)
            for d, v in sorted(diff_scores.items())
        }

    return EpisodeMetrics(
        agent_name=agent_name,
        total_emails=n,
        correct=correct,
        partial=partial,
        incorrect=incorrect,
        average_score=round(avg_score, 4),
        accuracy=round(accuracy, 4),
        macro_f1=macro_f1,
        weighted_f1=weighted_f1,
        per_class=per_class,
        per_difficulty=per_diff,
        confusion_matrix=cm,
    )