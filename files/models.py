"""
models.py — Type definitions for Email Sorting OpenEnv v2.0

Pydantic v2 when available; stdlib dataclasses fallback so the project
runs without ANY external dependencies installed.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict

try:
    from pydantic import BaseModel, Field
    _PYDANTIC = True
except ImportError:
    from dataclasses import dataclass as _dc, field as _df
    _PYDANTIC = False
    def Field(default=None, **_kw):
        return _df(default=default)
    class BaseModel:
        def __init_subclass__(cls, **kw):
            super().__init_subclass__(**kw)
            _dc(cls)
        def dict(self):
            import dataclasses
            return dataclasses.asdict(self)


# ── Enums ──────────────────────────────────────────────────────────────────

class EmailLabel(str, Enum):
    SPAM   = "spam"
    URGENT = "urgent"
    NORMAL = "normal"

class Difficulty(str, Enum):
    EASY   = "easy"
    MEDIUM = "medium"
    HARD   = "hard"


# ── Core step types ────────────────────────────────────────────────────────

class Observation(BaseModel):
    email_id:    int            = Field(0)
    email_text:  str            = Field("")
    subject:     Optional[str]  = Field(None)
    sender:      Optional[str]  = Field(None)
    difficulty:  Optional[str]  = Field(None)
    step_number: int            = Field(0)
    total_steps: int            = Field(0)
    # noise flag — True if this email was perturbed for robustness testing
    is_noisy:    bool           = Field(False)


class Action(BaseModel):
    label:      EmailLabel      = Field(EmailLabel.NORMAL)
    confidence: Optional[float] = Field(None)   # 0.0–1.0


class Reward(BaseModel):
    score:     float      = Field(0.0)
    predicted: EmailLabel = Field(EmailLabel.NORMAL)
    correct:   EmailLabel = Field(EmailLabel.NORMAL)
    rationale: str        = Field("")
    # shaped reward components (used by advanced grader)
    base_score:       float = Field(0.0)
    confidence_bonus: float = Field(0.0)


# ── Metrics ────────────────────────────────────────────────────────────────

class ClassMetrics(BaseModel):
    """Per-class precision / recall / F1."""
    label:     str   = Field("")
    precision: float = Field(0.0)
    recall:    float = Field(0.0)
    f1:        float = Field(0.0)
    support:   int   = Field(0)   # true count of this class in ground truth


class ConfusionMatrix(BaseModel):
    """3×3 confusion matrix stored as a nested dict."""
    labels: List[str]              = Field(default_factory=list)
    matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)

    @classmethod
    def build(cls, predictions: list, ground_truths: list) -> "ConfusionMatrix":
        labels = [e.value for e in EmailLabel]
        m: Dict[str, Dict[str, int]] = {
            true: {pred: 0 for pred in labels} for true in labels
        }
        for pred, true in zip(predictions, ground_truths):
            m[true.value][pred.value] += 1
        return cls(labels=labels, matrix=m)

    def as_table(self) -> str:
        """Pretty-print as a text table."""
        L = self.labels
        w = 10
        header = f"{'':>{w}}" + "".join(f"{l:>{w}}" for l in L)
        rows   = [header, "─" * (w * (len(L) + 1))]
        for true in L:
            row = f"{'T:'+true:>{w}}" + "".join(
                f"{self.matrix[true][pred]:>{w}}" for pred in L
            )
            rows.append(row)
        rows.append("")
        rows.append(f"{'':>{w}}" + "".join(f"{'P:'+l:>{w}}" for l in L))
        return "\n".join(rows)


class EpisodeMetrics(BaseModel):
    """Full evaluation report for one agent over one episode."""
    agent_name:       str             = Field("")
    total_emails:     int             = Field(0)
    correct:          int             = Field(0)
    partial:          int             = Field(0)
    incorrect:        int             = Field(0)
    average_score:    float           = Field(0.0)
    accuracy:         float           = Field(0.0)   # strict exact-match
    macro_f1:         float           = Field(0.0)
    weighted_f1:      float           = Field(0.0)
    per_class:        List[ClassMetrics]         = Field(default_factory=list)
    per_difficulty:   Dict[str, float]           = Field(default_factory=dict)
    confusion_matrix: Optional[ConfusionMatrix]  = Field(None)
    # robustness: score drop when noise is applied
    noise_delta:      Optional[float]            = Field(None)


# ── Leaderboard entry ──────────────────────────────────────────────────────

class LeaderboardEntry(BaseModel):
    rank:          int   = Field(0)
    agent_name:    str   = Field("")
    avg_score:     float = Field(0.0)
    accuracy:      float = Field(0.0)
    macro_f1:      float = Field(0.0)
    noise_delta:   Optional[float] = Field(None)
    badge:         str   = Field("")   # 🥇🥈🥉 etc.