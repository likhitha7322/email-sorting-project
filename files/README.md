# 📧 Email Sorting OpenEnv v2.0

> Production-grade AI environment for intelligent email triage — hackathon edition.

---

## 🏆 What's new in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Emails in dataset | 30 | **40** (12 easy / 14 medium / 14 hard) |
| Agents | 1 (rule-based) | **3** (rule-based → weighted scorer → ensemble) |
| Reward shaping | base only | **base + confidence bonus ±0.1** |
| Metrics | avg score | **accuracy, macro-F1, weighted-F1, per-class P/R/F1** |
| Confusion matrix | ❌ | **✅ 3×3 heatmap** |
| Noise robustness | ❌ | **✅ text perturbation + delta score** |
| Evaluation harness | manual | **`evaluate.py` — ranked leaderboard** |
| HTML report | ❌ | **`report.py` → zero-dependency `report.html`** |
| Action confidence | ❌ | **✅ optional `[0,1]` confidence field** |

---

## 🧩 Problem statement

Professionals waste hours triaging inboxes daily. This environment trains and benchmarks agents that classify emails into:

| Label | Description |
|-------|-------------|
| 🔴 `spam` | Unsolicited, promotional, or phishing mail |
| 🟡 `urgent` | Time-sensitive messages requiring immediate action |
| 🟢 `normal` | Routine, informational, or non-critical correspondence |

---

## 🏗️ Architecture

```
Email Queue (40 emails)
       │
       ▼
┌─────────────────┐   Observation   ┌──────────────────┐
│  EmailSorting   │ ──────────────► │   Your Agent     │
│    Env v2       │                 │  (or use ours)   │
│                 │ ◄────────────── │                  │
└─────────────────┘   Action        └──────────────────┘
       │ + confidence
       ▼
  Grader v2  →  Reward (base + confidence bonus)
       │
       ▼
  EpisodeMetrics  →  F1 / Confusion Matrix / Noise Delta
       │
       ▼
  report.py  →  report.html  (visual dashboard)
```

---

## 📁 Project structure

```
email-openenv/
├── env.py          ← OpenEnv environment (reset/step/state/render)
├── models.py       ← Pydantic types: Observation, Action, Reward,
│                     ClassMetrics, ConfusionMatrix, EpisodeMetrics
├── tasks.py        ← 40-email dataset (easy/medium/hard)
├── grader.py       ← Reward engine: base score + confidence shaping + F1
├── agents.py       ← 3 agents: RuleBased, WeightedScorer, Ensemble
├── baseline.py     ← Interactive step-by-step runner + leaderboard
├── evaluate.py     ← Full evaluation suite with noise robustness
├── report.py       ← HTML report generator (SVG charts, confusion matrix)
├── openenv.yaml    ← Environment specification
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 📐 Interface

### Observation
```python
class Observation(BaseModel):
    email_id:    int            # unique email identifier
    email_text:  str            # raw email body
    subject:     Optional[str]
    sender:      Optional[str]
    difficulty:  Optional[str]  # "easy" | "medium" | "hard"
    step_number: int
    total_steps: int
    is_noisy:    bool           # True when noise injection is active
```

### Action
```python
class Action(BaseModel):
    label:      EmailLabel      # "spam" | "urgent" | "normal"
    confidence: Optional[float] # [0.0–1.0]  ← new in v2
```

### Reward
```python
class Reward(BaseModel):
    score:            float      # final score (0.0–1.0)
    base_score:       float      # 0.0 / 0.5 / 1.0
    confidence_bonus: float      # ±0.1 shaped by confidence
    predicted:        EmailLabel
    correct:          EmailLabel
    rationale:        str
```

### Reward shaping

| Situation | Base | Confidence bonus | Final |
|-----------|------|-----------------|-------|
| Correct, confidence=0.9 | 1.0 | +0.09 | **1.0** (capped) |
| Correct, no confidence | 1.0 | 0 | **1.0** |
| urgent↔normal, conf=0.7 | 0.5 | −0.07 | **0.43** |
| spam↔urgent, conf=0.9 | 0.0 | −0.09 | **0.0** (floored) |

---

## 🤖 Agents

### RuleBasedAgent  —  score 0.8250 · F1 0.7968
Priority keyword matching: spam keywords → urgent keywords → default normal.
No confidence output. Strong on easy tier (1.00), weaker on hard (0.68).

### WeightedScorerAgent  —  score 0.8572 · F1 0.8222
Weighted keyword scoring. Each keyword has a calibrated weight.
Score gap between classes drives confidence output.
Excellent on hard tier (0.96), weaker on ambiguous medium cases.

### EnsembleAgent  —  score **0.9179** · F1 **0.8836**  🏆
Combines weighted scoring with domain heuristics:
- Suspicious domain regex → hard spam decision
- Trusted sender list → suppresses false-positive spam
- Time-pressure regex → catches implicit urgency
- Confidence-scaled output at every step

---

## 🚀 Setup

```bash
# Clone / unzip, then:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Run commands

```bash
# Step-by-step output for all 3 agents
python baseline.py

# Leaderboard only (fast)
python baseline.py --compare

# Single agent
python baseline.py --agent EnsembleAgent

# Filter by difficulty
python baseline.py --difficulty hard

# Enable noise injection
python baseline.py --noise

# Full evaluation suite (all metrics + noise robustness)
python evaluate.py

# Single-agent evaluation
python evaluate.py --agent EnsembleAgent

# Generate HTML report
python report.py                        # → report.html
python report.py --agent EnsembleAgent  # single agent
```

### Docker

```bash
docker build -t email-openenv .
docker run --rm email-openenv                            # leaderboard
docker run --rm email-openenv python evaluate.py         # full eval
docker run --rm -v $(pwd):/app/out email-openenv \
  python report.py --out out/report.html                 # HTML report
```

---

## 🔬 Programmatic usage

```python
from env import EmailSortingEnv
from agents import EnsembleAgent

env   = EmailSortingEnv(difficulty="hard", noise=True)
agent = EnsembleAgent()

obs = env.reset()
while obs is not None:
    action = agent.predict(obs)
    obs, reward, done, info = env.step(action)

metrics = info["episode_metrics"]
print(f"Score:    {metrics.average_score:.4f}")
print(f"Accuracy: {metrics.accuracy:.4f}")
print(f"Macro F1: {metrics.macro_f1:.4f}")
print(metrics.confusion_matrix.as_table())
```

### Build your own agent

```python
from models import Action, EmailLabel, Observation

class MyLLMAgent:
    name = "MyLLMAgent"

    def predict(self, obs: Observation) -> Action:
        # Call your model here
        label = EmailLabel.NORMAL
        confidence = 0.85
        return Action(label=label, confidence=confidence)
```

---

## 📊 Benchmark results

```
════════════════════════════════════════════════
  AGENT LEADERBOARD — Email Sorting OpenEnv v2
════════════════════════════════════════════════

  🥇 EnsembleAgent        0.9179  acc=0.875  F1=0.884
  🥈 WeightedScorerAgent  0.8572  acc=0.825  F1=0.822
  🥉 RuleBasedAgent       0.8250  acc=0.800  F1=0.797

  EnsembleAgent confusion matrix:
              P:spam  P:urgent  P:normal
  T:spam          9         0         1
  T:urgent        0        11         3
  T:normal        0         1        15

  Per-class F1:
    SPAM    0.9474  (precision=1.00  recall=0.90)
    URGENT  0.8462  (precision=0.92  recall=0.79)
    NORMAL  0.8571  (precision=0.79  recall=0.94)
```

---

## 📄 License

MIT — free to use, modify, and submit.

---

## 👥 Authors

OpenEnv Hackathon Team — built with ❤️ for the OpenEnv Challenge.