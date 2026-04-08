from __future__ import annotations
import argparse
import sys
from collections import defaultdict
from typing import List   # ✅ FIX ADDED

from env import EmailSortingEnv
from Agents import ALL_AGENTS, get_agent
from models import EmailLabel, EpisodeMetrics, LeaderboardEntry


# ── ANSI colour helpers ────────────────────────────────────────────────────

USE_COL = sys.stdout.isatty()

def _c(code, t): return f"\033[{code}m{t}\033[0m" if USE_COL else t

R = lambda t: _c("31", t)
G = lambda t: _c("32", t)
Y = lambda t: _c("33", t)
B = lambda t: _c("36", t)
BOLD = lambda t: _c("1",  t)
DIM  = lambda t: _c("2",  t)

SCORE_COL = lambda s: G(f"{s:.4f}") if s >= 0.85 else Y(f"{s:.4f}") if s >= 0.65 else R(f"{s:.4f}")


# ── Core runner ────────────────────────────────────────────────────────────

def run_agent(agent, difficulty=None, noise=False) -> EpisodeMetrics:
    """Run one full episode and return EpisodeMetrics."""
    env = EmailSortingEnv(difficulty=difficulty, noise=noise)
    obs = env.reset()
    while obs is not None:
        action = agent.predict(obs)
        obs, _, done, info = env.step(action)
    m = info["episode_metrics"]
    m.agent_name = agent.name
    return m


# ── Display helpers ────────────────────────────────────────────────────────

def print_metrics_table(m: EpisodeMetrics):
    print(BOLD(f"\n  Agent: {m.agent_name}"))
    print("  " + "─" * 54)
    print(f"  {'Emails':20s}: {m.total_emails}")
    print(f"  {'Avg reward score':20s}: {SCORE_COL(m.average_score)}")
    print(f"  {'Accuracy':20s}: {SCORE_COL(m.accuracy)}")
    print(f"  {'Macro F1':20s}: {SCORE_COL(m.macro_f1)}")
    print(f"  {'Weighted F1':20s}: {SCORE_COL(m.weighted_f1)}")
    print(f"  {'Correct (1.0)':20s}: {G(str(m.correct))}")
    print(f"  {'Partial (0.5)':20s}: {Y(str(m.partial))}")
    print(f"  {'Incorrect (0.0)':20s}: {R(str(m.incorrect))}")

    if m.per_class:
        print(f"\n  {'Class':10s}  {'Precision':>10}  {'Recall':>8}  {'F1':>8}  {'Support':>8}")
        print("  " + "─" * 54)
        for pc in m.per_class:
            name = pc.label.upper()
            print(f"  {name:10s}  {pc.precision:>10.4f}  {pc.recall:>8.4f}  {pc.f1:>8.4f}  {pc.support:>8}")

    if m.per_difficulty:
        print(f"\n  {'Difficulty':12s}  {'Avg Score':>10}")
        print("  " + "─" * 28)
        icons = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        for diff, score in sorted(m.per_difficulty.items()):
            icon = icons.get(diff, "  ")
            print(f"  {icon} {diff:9s}  {SCORE_COL(score)}")

    if m.confusion_matrix:
        print(f"\n  Confusion Matrix  (rows=True, cols=Predicted)")
        print("  " + "─" * 38)
        L   = m.confusion_matrix.labels
        mat = m.confusion_matrix.matrix
        hdr = f"  {'':>10}" + "".join(f"{'P:'+l:>10}" for l in L)
        print(hdr)
        for true in L:
            row = f"  {'T:'+true:>10}"
            for pred in L:
                val = mat[true][pred]
                if true == pred:
                    row += G(f"{val:>10}")
                elif val > 0:
                    row += R(f"{val:>10}")
                else:
                    row += f"{val:>10}"
            print(row)

    if m.noise_delta is not None:
        delta_str = f"{m.noise_delta:+.4f}"
        col = R if m.noise_delta < -0.05 else Y if m.noise_delta < 0 else G
        print(f"\n  {'Noise robustness':20s}: {col(delta_str)}  (score with noise − clean)")
    print()


def print_leaderboard(entries: List[LeaderboardEntry]):
    print(BOLD(B("\n  ╔══════════════════════════════════════════════════════════╗")))
    print(BOLD(B("  ║            AGENT LEADERBOARD — Email Sorting OpenEnv     ║")))
    print(BOLD(B("  ╚══════════════════════════════════════════════════════════╝")))
    print()
    print(f"  {'Rank':>6}  {'Agent':25s}  {'AvgScore':>9}  {'Accuracy':>9}  {'MacroF1':>8}  {'NoiseDelta':>11}")
    print("  " + "─" * 78)
    for e in entries:
        nd = f"{e.noise_delta:+.4f}" if e.noise_delta is not None else "   n/a  "
        nd_col = R if (e.noise_delta or 0) < -0.05 else Y if (e.noise_delta or 0) < 0 else G
        print(
            f"  {e.badge:>4} #{e.rank:<2}  {e.agent_name:25s}"
            f"  {SCORE_COL(e.avg_score):>9}  {SCORE_COL(e.accuracy):>9}"
            f"  {SCORE_COL(e.macro_f1):>8}  {nd_col(nd):>11}"
        )
    print()


# ── Main evaluation loop ───────────────────────────────────────────────────

def evaluate(
    agent_filter: str | None = None,
    difficulty:   str | None = None,
    run_noise:    bool = True,
):
    print()
    print(BOLD(B("════════════════════════════════════════════════════════════")))
    print(BOLD(B("       Email Sorting OpenEnv v2.0 — Full Evaluation Suite   ")))
    print(BOLD(B("════════════════════════════════════════════════════════════")))

    agents = [cls() for cls in ALL_AGENTS]
    if agent_filter:
        agents = [a for a in agents if a.name.lower() == agent_filter.lower()]
        if not agents:
            print(R(f"\n  Agent '{agent_filter}' not found."))
            sys.exit(1)

    leaderboard: List[LeaderboardEntry] = []   # ✅ FIXED
    all_metrics: List[EpisodeMetrics]   = []   # ✅ FIXED

    for agent in agents:
        print(BOLD(f"\n{'─'*60}"))
        print(BOLD(f"  Evaluating: {B(agent.name)}"))
        print(f"{'─'*60}")

        clean_m = run_agent(agent, difficulty=difficulty, noise=False)
        all_metrics.append(clean_m)
        print_metrics_table(clean_m)

        noise_delta = None
        if run_noise:
            noisy_m   = run_agent(agent, difficulty=difficulty, noise=True)
            noise_delta = round(noisy_m.average_score - clean_m.average_score, 4)
            clean_m.noise_delta = noise_delta
            print(f"  {DIM('Noise test:')} score dropped {R(f'{noise_delta:+.4f}') if noise_delta < 0 else G(f'{noise_delta:+.4f}')}")

        leaderboard.append(LeaderboardEntry(
            agent_name  = agent.name,
            avg_score   = clean_m.average_score,
            accuracy    = clean_m.accuracy,
            macro_f1    = clean_m.macro_f1,
            noise_delta = noise_delta,
        ))

    leaderboard.sort(key=lambda e: e.avg_score, reverse=True)
    badges = ["🥇", "🥈", "🥉"] + ["  "] * 10
    for i, e in enumerate(leaderboard):
        e.rank  = i + 1
        e.badge = badges[i]

    print_leaderboard(leaderboard)

    best = leaderboard[0]
    print(BOLD(G(f"  ✔ Best agent: {best.agent_name}  —  avg score {best.avg_score:.4f}  |  macro-F1 {best.macro_f1:.4f}")))
    print()


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Evaluate all agents on Email Sorting OpenEnv.")
    p.add_argument("--agent",      default=None, help="Run only this agent by name")
    p.add_argument("--difficulty", default=None, choices=["easy","medium","hard"])
    p.add_argument("--no-noise",   action="store_true", help="Skip noise robustness test")
    args = p.parse_args()
    evaluate(
        agent_filter = args.agent,
        difficulty   = args.difficulty,
        run_noise    = not args.no_noise,
    )