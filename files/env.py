"""
env.py — Email Sorting OpenEnv v2.0

OpenEnv interface:
  reset(difficulty, noise)  → Observation
  step(action)              → (Observation|None, Reward, done, info)
  state()                   → dict
  render()                  → str
  close()

New in v2.0
───────────
  • Noise injection: randomly perturbs email text for robustness testing
  • Episode history: full trace of every step
  • Typed EpisodeMetrics returned in info at episode end
  • render_summary() for a polished multi-line summary block
"""

from __future__ import annotations
import logging
import random
import re
from typing import Optional

from models import Action, EmailLabel, Observation, Reward
from tasks import TASKS, get_all_tasks, get_tasks_by_difficulty
from grader import grade

logging.basicConfig(
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARNING,   # quiet by default; set to INFO for verbose mode
)
logger = logging.getLogger(__name__)

# ── Noise helpers ──────────────────────────────────────────────────────────

_NOISE_SUBSTITUTIONS = [
    # Obfuscate obvious spam keywords
    ("free",    "fr3e"),
    ("win",     "w1n"),
    ("urgent",  "urg3nt"),
    ("asap",    "a.s.a.p"),
    ("click",   "cl1ck"),
    ("offer",   "0ffer"),
    ("prize",   "pr1ze"),
    ("immediately", "immediat3ly"),
]

def _inject_noise(text: str, seed: int = 0) -> str:
    """
    Lightly perturb email text to test agent robustness.
    Applies a subset of substitutions so keyword matchers degrade gracefully.
    """
    rng = random.Random(seed)
    result = text
    # Apply 2–4 random substitutions
    subs = rng.sample(_NOISE_SUBSTITUTIONS, k=min(4, len(_NOISE_SUBSTITUTIONS)))
    for old, new in subs:
        result = re.sub(old, new, result, flags=re.IGNORECASE)
    # Randomly drop a sentence (split on ". ")
    sentences = result.split(". ")
    if len(sentences) > 2:
        drop_idx = rng.randint(0, len(sentences) - 1)
        sentences.pop(drop_idx)
        result = ". ".join(sentences)
    return result


# ── Environment ────────────────────────────────────────────────────────────

class EmailSortingEnv:
    """
    Step-based OpenEnv environment for email classification.

    Usage
    ─────
    env = EmailSortingEnv()
    obs = env.reset()
    while obs is not None:
        action = agent.predict(obs)
        obs, reward, done, info = env.step(action)
    metrics = info["episode_metrics"]   # EpisodeMetrics when done=True
    """

    METADATA = {
        "name":         "EmailSortingEnv-v2",
        "version":      "2.0.0",
        "description":  "Classify emails: spam / urgent / normal",
        "obs_space":    {"email_text": "str", "subject": "str", "sender": "str",
                         "difficulty": "str", "is_noisy": "bool"},
        "act_space":    {"label": ["spam", "urgent", "normal"],
                         "confidence": "float [0,1] optional"},
        "reward_range": [0.0, 1.0],
        "reward_shaping": "confidence bonus ±0.1",
    }

    def __init__(
        self,
        difficulty: Optional[str] = None,
        noise: bool = False,
        shuffle: bool = False,
        seed: int = 42,
        verbose: bool = False,
    ):
        self._base_tasks = (
            get_tasks_by_difficulty(difficulty) if difficulty else get_all_tasks()
        )
        self._noise   = noise
        self._shuffle = shuffle
        self._seed    = seed
        if verbose:
            logging.getLogger().setLevel(logging.INFO)

        # episode state
        self._tasks:    list  = []
        self._step:     int   = 0
        self._rewards:  list  = []
        self._actions:  list  = []
        self._done:     bool  = True
        self._difficulty_filter = difficulty

        logger.info(
            "EmailSortingEnv-v2 ready — %d tasks (difficulty=%s, noise=%s)",
            len(self._base_tasks), difficulty or "all", noise,
        )

    # ── Public API ─────────────────────────────────────────────────────────

    def reset(self) -> Observation:
        tasks = list(self._base_tasks)
        if self._shuffle:
            random.Random(self._seed).shuffle(tasks)
        self._tasks   = tasks
        self._step    = 0
        self._rewards = []
        self._actions = []
        self._done    = False
        logger.info("Episode reset — %d emails queued.", len(tasks))
        return self._make_observation()

    def step(self, action: Action) -> tuple:
        """
        Returns (next_obs | None, reward, done, info).
        info["episode_metrics"] is populated when done=True.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        task          = self._tasks[self._step]
        correct_label = EmailLabel(task["label"])
        reward        = grade(action, correct_label)

        self._rewards.append(reward)
        self._actions.append(action)

        logger.info(
            "Step %02d  pred=%-7s  truth=%-7s  score=%.2f",
            self._step + 1, action.label, correct_label.value, reward.score,
        )

        self._step += 1
        done = self._step >= len(self._tasks)
        self._done = done

        if done:
            info = self._build_episode_info()
            logger.info("Episode complete — avg %.4f", info["average_score"])
            return None, reward, True, info

        return self._make_observation(), reward, False, {
            "step": self._step,
            "last_score": reward.score,
        }

    def state(self) -> dict:
        scores = [r.score for r in self._rewards]
        return {
            "current_step":  self._step,
            "total_steps":   len(self._tasks),
            "done":          self._done,
            "noise":         self._noise,
            "scores_so_far": scores,
            "running_avg":   round(sum(scores)/len(scores), 4) if scores else None,
        }

    def render(self) -> str:
        s = self.state()
        avg = s["running_avg"] or 0.0
        bar = "█" * int(20 * avg) + "░" * (20 - int(20 * avg))
        return (
            f"╔══════════════════════════════════╗\n"
            f"║  EmailSortingEnv-v2              ║\n"
            f"╠══════════════════════════════════╣\n"
            f"║  Step  : {s['current_step']:>3} / {s['total_steps']:<3}            ║\n"
            f"║  Done  : {str(s['done']):<26}║\n"
            f"║  Noise : {str(s['noise']):<26}║\n"
            f"║  Avg   : {avg:<5.3f}  {bar} ║\n"
            f"╚══════════════════════════════════╝"
        )

    def close(self) -> None:
        logger.info("Environment closed.")

    # ── Private helpers ────────────────────────────────────────────────────

    def _make_observation(self) -> Observation:
        task    = self._tasks[self._step]
        is_noisy = self._noise
        body    = task["body"]
        subject = task.get("subject")
        if is_noisy:
            body    = _inject_noise(body,    seed=self._seed + self._step)
            subject = _inject_noise(subject, seed=self._seed + self._step + 100) if subject else subject
        return Observation(
            email_id    = task["email_id"],
            email_text  = body,
            subject     = subject,
            sender      = task.get("sender"),
            difficulty  = task.get("difficulty"),
            step_number = self._step,
            total_steps = len(self._tasks),
            is_noisy    = is_noisy,
        )

    def _build_episode_info(self) -> dict:
        from grader import grade_episode as _ge
        difficulties = [t.get("difficulty") for t in self._tasks]
        metrics = _ge(
            predictions   = self._actions,
            ground_truths = [EmailLabel(t["label"]) for t in self._tasks],
            difficulties  = difficulties,
            agent_name    = "agent",
        )
        scores = [r.score for r in self._rewards]
        return {
            "average_score":    metrics.average_score,
            "accuracy":         metrics.accuracy,
            "macro_f1":         metrics.macro_f1,
            "weighted_f1":      metrics.weighted_f1,
            "correct":          metrics.correct,
            "partial":          metrics.partial,
            "incorrect":        metrics.incorrect,
            "per_difficulty":   metrics.per_difficulty,
            "per_class":        metrics.per_class,
            "confusion_matrix": metrics.confusion_matrix,
            "episode_metrics":  metrics,
            "step":             self._step,
        }