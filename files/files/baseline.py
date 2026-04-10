"""
baseline.py — Rule-based baseline agent for Email Sorting OpenEnv.

Strategy
────────
  1. Check for spam keywords → label as SPAM
  2. Check for urgency keywords → label as URGENT
  3. Default to NORMAL

Run directly:
  python baseline.py
  python baseline.py --difficulty easy
  python baseline.py --difficulty hard
"""

import argparse
import sys
from collections import defaultdict

from models import Action, EmailLabel
from env import EmailSortingEnv

# ---------------------------------------------------------------------------
# ANSI colour helpers (graceful fallback on Windows / no-TTY)
# ---------------------------------------------------------------------------

USE_COLOUR = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOUR else text

RED    = lambda t: _c("31", t)
GREEN  = lambda t: _c("32", t)
YELLOW = lambda t: _c("33", t)
CYAN   = lambda t: _c("36", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)


# ---------------------------------------------------------------------------
# Keyword lists
# ---------------------------------------------------------------------------

SPAM_KEYWORDS = [
    "win", "winner", "won", "free", "offer", "exclusive", "click here",
    "claim", "prize", "lottery", "discount", "cheap", "buy now",
    "unsubscribe ignored", "no prescription", "pills", "pharmacy",
    "limited time", "act fast", "verify your", "account suspended",
    "paypa1", "google-security-alert", "fedex-delivery-notification",
    "loyaltyclubz", "freeiphonez", "prizewinners",
]

URGENCY_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "right away",
    "emergency", "p0", "incident", "breach", "down", "failure",
    "action required", "action needed", "as soon as possible",
    "by tomorrow", "by today", "by eod", "within 24 hours",
    "within 3 days", "before expiry", "do not ignore",
    "must be submitted", "non-submission", "payment failed",
]


# ---------------------------------------------------------------------------
# Baseline Agent
# ---------------------------------------------------------------------------

class RuleBasedAgent:
    """
    A simple heuristic agent that classifies emails via keyword matching.

    Priority:  spam > urgent > normal
    """

    def __init__(self):
        self.predictions: list[Action] = []

    def predict(self, observation) -> Action:
        """Classify a single email observation."""
        # Combine subject and body into one searchable blob
        haystack = " ".join([
            (observation.subject  or ""),
            (observation.sender   or ""),
            (observation.email_text or ""),
        ]).lower()

        # 1. Spam check
        for kw in SPAM_KEYWORDS:
            if kw in haystack:
                return Action(label=EmailLabel.SPAM)

        # 2. Urgency check
        for kw in URGENCY_KEYWORDS:
            if kw in haystack:
                return Action(label=EmailLabel.URGENT)

        # 3. Default
        return Action(label=EmailLabel.NORMAL)


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

LABEL_COLOUR = {
    "spam":   RED,
    "urgent": YELLOW,
    "normal": GREEN,
}

def _label_str(label: str) -> str:
    colour = LABEL_COLOUR.get(label, lambda x: x)
    return colour(f"[{label.upper():>6}]")

def _score_str(score: float) -> str:
    if score == 1.0:
        return GREEN(f"✔  {score:.1f}")
    elif score == 0.5:
        return YELLOW(f"~  {score:.1f}")
    else:
        return RED(f"✘  {score:.1f}")


def print_banner():
    print()
    print(BOLD(CYAN("╔══════════════════════════════════════════════════════════════╗")))
    print(BOLD(CYAN("║          Email Sorting OpenEnv — Baseline Agent              ║")))
    print(BOLD(CYAN("╚══════════════════════════════════════════════════════════════╝")))
    print()


def print_step_result(step_num: int, obs, action, reward):
    subject    = (obs.subject or "(no subject)")[:55]
    predicted  = _label_str(action.label)
    correct    = _label_str(reward.correct)
    score      = _score_str(reward.score)
    difficulty_tag = DIM(f"[{obs.email_id:02d}]")

    print(f"  {difficulty_tag} Step {step_num:02d}  {BOLD(subject)}")
    print(f"         Predicted : {predicted}   Correct : {correct}   Score : {score}")
    if reward.score < 1.0:
        print(f"         {DIM('→ ' + reward.rationale)}")
    print()


def print_summary(stats: dict, per_difficulty: dict):
    avg   = stats["average_score"]
    total = stats["total_steps"]

    bar_len  = 30
    filled   = int(bar_len * avg)
    bar      = "█" * filled + "░" * (bar_len - filled)
    colour   = GREEN if avg >= 0.8 else YELLOW if avg >= 0.5 else RED

    print(BOLD("─" * 64))
    print(BOLD("  EPISODE SUMMARY"))
    print("─" * 64)
    print(f"  Total emails     : {total}")
    print(f"  Correct  (1.0)   : {GREEN(str(stats['correct']))}")
    print(f"  Partial  (0.5)   : {YELLOW(str(stats['partial']))}")
    print(f"  Incorrect (0.0)  : {RED(str(stats['incorrect']))}")
    print()
    print(f"  Average Score    : {colour(f'{avg:.4f}')}  {colour(bar)}")
    print()

    if per_difficulty:
        print(BOLD("  Accuracy by Difficulty"))
        print("  " + "─" * 40)
        for diff, data in sorted(per_difficulty.items()):
            d_avg = data["score"] / data["count"] if data["count"] else 0.0
            icon  = "🟢" if d_avg >= 0.8 else "🟡" if d_avg >= 0.5 else "🔴"
            print(f"  {icon}  {diff.upper():6s}  →  {d_avg:.4f}  ({data['count']} emails)")
        print()

    print(BOLD("─" * 64))
    print()


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(difficulty: str | None = None):
    print_banner()

    env   = EmailSortingEnv(difficulty=difficulty)
    agent = RuleBasedAgent()

    obs = env.reset()
    print(f"  Loaded {BOLD(str(env.state()['total_steps']))} emails", end="")
    if difficulty:
        print(f" (difficulty = {BOLD(difficulty)})", end="")
    print("\n")

    step_num       = 1
    all_rewards    = []
    per_difficulty = defaultdict(lambda: {"score": 0.0, "count": 0})

    while obs is not None:
        action              = agent.predict(obs)
        next_obs, reward, done, info = env.step(action)

        # Look up the difficulty of the current task for per-difficulty stats
        from tasks import TASKS
        task_diff = next(
            (t["difficulty"] for t in TASKS if t["email_id"] == obs.email_id),
            "unknown",
        )

        all_rewards.append(reward)
        per_difficulty[task_diff]["score"] += reward.score
        per_difficulty[task_diff]["count"] += 1

        print_step_result(step_num, obs, action, reward)
        step_num += 1
        obs = next_obs

    # Final summary
    scores = [r.score for r in all_rewards]
    stats = {
        "average_score": sum(scores) / len(scores),
        "total_steps":   len(scores),
        "correct":       sum(1 for r in all_rewards if r.score == 1.0),
        "partial":       sum(1 for r in all_rewards if r.score == 0.5),
        "incorrect":     sum(1 for r in all_rewards if r.score == 0.0),
    }
    print_summary(stats, per_difficulty)

    return stats["average_score"]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Email Sorting baseline agent.")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default=None,
        help="Filter to a specific difficulty level (default: all levels).",
    )
    args = parser.parse_args()
    run(difficulty=args.difficulty)
