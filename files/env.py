from __future__ import annotations
import logging
import random
import re
from typing import Optional

from models import Action, EmailLabel, Observation, Reward
from tasks import get_all_tasks, get_tasks_by_difficulty
from grader import grade

logging.basicConfig(
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)

# ── Noise helpers ──────────────────────────────────────────────────────────

_NOISE_SUBSTITUTIONS = [
    ("free", "fr3e"),
    ("win", "w1n"),
    ("urgent", "urg3nt"),
    ("asap", "a.s.a.p"),
    ("click", "cl1ck"),
    ("offer", "0ffer"),
    ("prize", "pr1ze"),
    ("immediately", "immediat3ly"),
]

def _inject_noise(text: str, seed: int = 0) -> str:
    if not text:
        return text

    rng = random.Random(seed)
    result = text

    subs = rng.sample(_NOISE_SUBSTITUTIONS, k=min(4, len(_NOISE_SUBSTITUTIONS)))
    for old, new in subs:
        result = re.sub(old, new, result, flags=re.IGNORECASE)

    sentences = result.split(". ")
    if len(sentences) > 2:
        sentences.pop(rng.randint(0, len(sentences) - 1))
        result = ". ".join(sentences)

    return result


# ── Environment ────────────────────────────────────────────────────────────

class EmailSortingEnv:

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
        self._noise = noise
        self._shuffle = shuffle
        self._seed = seed

        if verbose:
            logging.getLogger().setLevel(logging.INFO)

        self._tasks = []
        self._step = 0
        self._rewards = []
        self._actions = []
        self._done = True
        self._difficulty_filter = difficulty

    # ✅ FIXED RESET (SAFE + COMPATIBLE)
    def reset(self, difficulty=None, noise=None) -> Observation:
        try:
            if difficulty is not None:
                self._base_tasks = get_tasks_by_difficulty(difficulty)
                self._difficulty_filter = difficulty

            if noise is not None:
                self._noise = noise

            tasks = list(self._base_tasks)

            if self._shuffle:
                random.Random(self._seed).shuffle(tasks)

            if not tasks:
                raise ValueError("No tasks available")

            self._tasks = tasks
            self._step = 0
            self._rewards = []
            self._actions = []
            self._done = False

            return self._make_observation()

        except Exception as e:
            logger.error(f"Reset failed: {e}")

            # fallback (prevents OpenEnv crash)
            return Observation(
                email_id="0",
                email_text="fallback",
                subject="",
                sender="",
                difficulty="easy",
                step_number=0,
                total_steps=1,
                is_noisy=False,
            )

    def step(self, action: Action) -> tuple:
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        task = self._tasks[self._step]
        correct_label = EmailLabel(task["label"])
        reward = grade(action, correct_label)

        self._rewards.append(reward)
        self._actions.append(action)

        self._step += 1
        done = self._step >= len(self._tasks)
        self._done = done

        if done:
            info = self._build_episode_info()
            return None, reward, True, info

        return self._make_observation(), reward, False, {
            "step": self._step,
            "last_score": reward.score,
        }

    def state(self) -> dict:
        scores = [r.score for r in self._rewards]
        return {
            "current_step": self._step,
            "total_steps": len(self._tasks),
            "done": self._done,
            "noise": self._noise,
            "scores_so_far": scores,
            "running_avg": round(sum(scores)/len(scores), 4) if scores else None,
        }

    def render(self) -> str:
        s = self.state()
        avg = s["running_avg"] or 0.0
        bar = "█" * int(20 * avg) + "░" * (20 - int(20 * avg))
        return (
            f"Step: {s['current_step']} / {s['total_steps']} | "
            f"Done: {s['done']} | Noise: {s['noise']} | Avg: {avg:.3f}\n{bar}"
        )

    def close(self) -> None:
        logger.info("Environment closed.")

    # ── Helpers ────────────────────────────────────────────────────────────

    def _make_observation(self) -> Observation:
        task = self._tasks[self._step]

        body = task.get("body", "")
        subject = task.get("subject")

        if self._noise:
            body = _inject_noise(body, seed=self._seed + self._step)
            if subject:
                subject = _inject_noise(subject, seed=self._seed + self._step + 100)

        return Observation(
            email_id=task.get("email_id", "0"),
            email_text=body,
            subject=subject,
            sender=task.get("sender"),
            difficulty=task.get("difficulty"),
            step_number=self._step,
            total_steps=len(self._tasks),
            is_noisy=self._noise,
        )

    def _build_episode_info(self) -> dict:
        from grader import grade_episode

        metrics = grade_episode(
            predictions=self._actions,
            ground_truths=[EmailLabel(t["label"]) for t in self._tasks],
            difficulties=[t.get("difficulty") for t in self._tasks],
            agent_name="agent",
        )

        return {
            "average_score": metrics.average_score,
            "accuracy": metrics.accuracy,
            "macro_f1": metrics.macro_f1,
            "weighted_f1": metrics.weighted_f1,
            "correct": metrics.correct,
            "partial": metrics.partial,
            "incorrect": metrics.incorrect,
            "per_difficulty": metrics.per_difficulty,
            "per_class": metrics.per_class,
            "confusion_matrix": metrics.confusion_matrix,
            "episode_metrics": metrics,
            "step": self._step,
        }