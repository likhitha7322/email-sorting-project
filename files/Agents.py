"""
agents.py — Multiple agent implementations for Email Sorting OpenEnv v2.0

Three agents, increasing sophistication:

  RuleBasedAgent        — priority keyword matching  (baseline)
  WeightedScorerAgent   — weighted keyword scoring + confidence
  EnsembleAgent         — combines multiple signals + meta-rules
"""

from __future__ import annotations
import re
from models import Action, EmailLabel, Observation


# ═══════════════════════════════════════════════════════════════════════════
#  Agent 1 — Rule-Based  (simple keyword priority)
# ═══════════════════════════════════════════════════════════════════════════

SPAM_KW = [
    "win", "winner", "won", "free", "offer", "exclusive", "click here",
    "claim", "prize", "lottery", "discount", "cheap", "buy now",
    "unsubscribe ignored", "no prescription", "pills", "pharmacy",
    "limited time", "act fast", "verify your", "account suspended",
    "paypa1", "google-security-alert", "fedex-delivery-notification",
    "loyaltyclubz", "freeiphonez", "prizewinners", "fast-cash",
    "make money fast", "work from home", "earn $",
]

URGENT_KW = [
    "urgent", "asap", "immediately", "critical", "right away",
    "emergency", "p0 incident", "breach", "server down", "failure",
    "action required", "action needed", "as soon as possible",
    "by tomorrow", "by today", "by eod", "within 24 hours",
    "within 3 days", "before expiry", "do not ignore",
    "must be submitted", "non-submission", "payment failed",
    "must be patched", "regulatory action", "end of business",
    "close of business", "before your start date",
]


class RuleBasedAgent:
    """Priority keyword matcher: spam > urgent > normal."""

    name = "RuleBasedAgent"

    def predict(self, obs: Observation) -> Action:
        hay = (
            f"{obs.subject or ''} {obs.sender or ''} {obs.email_text}"
        ).lower()

        for kw in SPAM_KW:
            if kw in hay:
                return Action(label=EmailLabel.SPAM)
        for kw in URGENT_KW:
            if kw in hay:
                return Action(label=EmailLabel.URGENT)
        return Action(label=EmailLabel.NORMAL)


# ═══════════════════════════════════════════════════════════════════════════
#  Agent 2 — Weighted Scorer  (scored matching + calibrated confidence)
# ═══════════════════════════════════════════════════════════════════════════

# (keyword, weight) pairs — higher weight = stronger signal
SPAM_WEIGHTED = [
    ("win", 3.0), ("winner", 3.5), ("lottery", 4.0), ("prize", 3.5),
    ("free", 1.5), ("click here", 2.5), ("claim", 2.0), ("offer", 1.0),
    ("discount", 1.5), ("cheap", 2.0), ("buy now", 2.5), ("no prescription", 4.0),
    ("pills", 3.0), ("make money fast", 5.0), ("earn $", 3.0), ("act fast", 2.0),
    ("paypa1", 5.0), ("google-security-alert", 5.0), ("fedex-delivery-notification", 5.0),
    ("unsubscribe ignored", 4.0), ("work from home", 2.5), ("fast-cash", 4.5),
]

URGENT_WEIGHTED = [
    ("urgent", 3.0), ("asap", 2.5), ("immediately", 2.5), ("critical", 2.5),
    ("emergency", 3.0), ("p0 incident", 5.0), ("breach", 4.0), ("server down", 4.5),
    ("action required", 3.0), ("action needed", 2.5), ("payment failed", 3.0),
    ("by eod", 2.5), ("do not ignore", 3.5), ("regulatory action", 4.5),
    ("non-submission", 4.0), ("must be patched", 4.5), ("close of business", 3.5),
    ("end of business today", 4.0), ("sign by friday", 3.5), ("before start date", 3.0),
    ("no later than", 3.5), ("merger timeline", 4.0), ("board meeting", 2.5),
    ("within 48 hours", 3.0), ("within 24 hours", 3.0),
]


class WeightedScorerAgent:
    """
    Computes a spam-score and urgent-score via weighted keyword matching.
    Returns a calibrated confidence based on the score gap between classes.
    """

    name = "WeightedScorerAgent"
    SPAM_THRESHOLD   = 3.0
    URGENT_THRESHOLD = 2.5

    def predict(self, obs: Observation) -> Action:
        hay = (
            f"{obs.subject or ''} {obs.sender or ''} {obs.email_text}"
        ).lower()

        spam_score   = sum(w for kw, w in SPAM_WEIGHTED   if kw in hay)
        urgent_score = sum(w for kw, w in URGENT_WEIGHTED if kw in hay)

        # Compute confidence from normalised score
        def conf(score: float, threshold: float) -> float:
            if score == 0:
                return 0.0
            return round(min(1.0, score / (threshold * 2)), 2)

        if spam_score >= self.SPAM_THRESHOLD and spam_score >= urgent_score:
            return Action(label=EmailLabel.SPAM, confidence=conf(spam_score, self.SPAM_THRESHOLD))

        if urgent_score >= self.URGENT_THRESHOLD:
            return Action(label=EmailLabel.URGENT, confidence=conf(urgent_score, self.URGENT_THRESHOLD))

        return Action(label=EmailLabel.NORMAL, confidence=0.7)


# ═══════════════════════════════════════════════════════════════════════════
#  Agent 3 — Ensemble  (weighted + heuristic meta-rules)
# ═══════════════════════════════════════════════════════════════════════════

# Suspicious domain patterns that strongly indicate phishing/spam
SUSPICIOUS_DOMAINS = re.compile(
    r"paypa1|google-security-alert|fedex-delivery-notification"
    r"|freeiphonez|prizewinners|fast-cash|loyaltyclubz|health99"
    r"|spammer-central|no-rx-pharmacy",
    re.IGNORECASE,
)

# Trusted sender domains — reduce false-positive spam rate
TRUSTED_DOMAINS = re.compile(
    r"@(company\.com|aws\.amazon\.com|adobe\.com|netflix\.com"
    r"|regulatory-body\.gov|lawfirm\.com|startup\.io|toptech\.com"
    r"|gmail\.com|substack\.com)",
    re.IGNORECASE,
)

# Time-pressure phrases that indicate urgency even without explicit keyword
TIME_PRESSURE = re.compile(
    r"(by (eod|monday|tuesday|wednesday|thursday|friday)|"
    r"before (close|end|expiry|start date)|"
    r"no later than|merger timeline|board meeting|"
    r"within \d+ (hours?|days?))",
    re.IGNORECASE,
)


class EnsembleAgent:
    """
    Combines weighted scoring, sender-domain heuristics, and meta-rules
    to reduce false positives (especially spam false-positives on legit senders).
    """

    name = "EnsembleAgent"

    def __init__(self):
        self._scorer = WeightedScorerAgent()

    def predict(self, obs: Observation) -> Action:
        hay     = f"{obs.subject or ''} {obs.sender or ''} {obs.email_text}"
        hay_low = hay.lower()
        sender  = (obs.sender or "").lower()

        # Rule 0: Suspicious domain → hard spam
        if SUSPICIOUS_DOMAINS.search(hay):
            return Action(label=EmailLabel.SPAM, confidence=0.97)

        # Rule 1: Trusted sender → never spam
        is_trusted = bool(TRUSTED_DOMAINS.search(sender))

        # Get weighted scorer base decision
        base_action = self._scorer.predict(obs)
        base_label  = EmailLabel(base_action.label)

        # Rule 2: If scorer says spam but sender is trusted → override to urgent/normal
        if base_label == EmailLabel.SPAM and is_trusted:
            # Check if it feels urgent despite trusted sender
            if TIME_PRESSURE.search(hay) or any(
                kw in hay_low for kw in ["payment failed", "action required",
                                          "breach", "server down", "must be patched"]
            ):
                return Action(label=EmailLabel.URGENT, confidence=0.75)
            return Action(label=EmailLabel.NORMAL, confidence=0.72)

        # Rule 3: Catch time-pressure urgency the scorer might miss
        if base_label == EmailLabel.NORMAL and TIME_PRESSURE.search(hay):
            if not is_trusted and any(c in hay_low for c in ["$", "free", "prize"]):
                pass  # Likely spam with time pressure — keep normal or let scorer decide
            else:
                return Action(label=EmailLabel.URGENT, confidence=0.68)

        # Rule 4: High-confidence spam with trusted domain → bump to normal
        if base_label == EmailLabel.SPAM and (base_action.confidence or 0) < 0.5 and is_trusted:
            return Action(label=EmailLabel.NORMAL, confidence=0.65)

        return base_action


# ── Factory ────────────────────────────────────────────────────────────────

ALL_AGENTS = [RuleBasedAgent, WeightedScorerAgent, EnsembleAgent]

def get_agent(name: str):
    for cls in ALL_AGENTS:
        if cls.name.lower() == name.lower():
            return cls()
    raise ValueError(f"Unknown agent '{name}'. Available: {[c.name for c in ALL_AGENTS]}")