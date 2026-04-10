"""
report.py — HTML report generator for Email Sorting OpenEnv v2.0

Generates a self-contained HTML file with:
  • Score summary cards
  • Per-difficulty bar chart (pure SVG — zero JS dependencies)
  • Confusion matrix heatmap (SVG)
  • Per-class metrics table
  • Full email-by-email results table
  • Leaderboard section if multiple agents are provided

Run:
  python report.py                     → report.html  (all agents, all emails)
  python report.py --agent Ensemble    → report.html  (one agent)
  python report.py --out results.html
"""

from __future__ import annotations
import argparse
import html
import os
from datetime import datetime

from env import EmailSortingEnv
from Agents import ALL_AGENTS, get_agent
from grader import grade_episode
from models import EmailLabel, EpisodeMetrics


# ── Run agent, collect per-step detail ────────────────────────────────────

def run_agent_detailed(agent, difficulty=None):
    env    = EmailSortingEnv(difficulty=difficulty)
    obs    = env.reset()
    steps  = []
    while obs is not None:
        action = agent.predict(obs)
        next_obs, reward, done, info = env.step(action)
        steps.append({
            "email_id":   obs.email_id,
            "subject":    obs.subject or "",
            "difficulty": obs.difficulty or "",
            "predicted":  str(action.label),
            "correct":    str(reward.correct),
            "score":      reward.score,
            "rationale":  reward.rationale,
        })
        obs = next_obs
    metrics = info["episode_metrics"]
    metrics.agent_name = agent.name
    return metrics, steps


# ── SVG helpers ────────────────────────────────────────────────────────────

def _bar_chart_svg(per_diff: dict) -> str:
    """Render per-difficulty bar chart as inline SVG."""
    if not per_diff:
        return ""
    colours = {"easy": "#22c55e", "medium": "#f59e0b", "hard": "#ef4444"}
    items   = sorted(per_diff.items())
    n       = len(items)
    W, H    = 400, 180
    pad_l, pad_r, pad_t, pad_b = 40, 20, 20, 40
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_t - pad_b
    bar_w   = chart_w // n - 16

    rects = []
    for i, (diff, score) in enumerate(items):
        x        = pad_l + i * (chart_w // n) + 8
        bar_h    = int(chart_h * score)
        y        = pad_t + chart_h - bar_h
        col      = colours.get(diff, "#6366f1")
        label    = html.escape(diff.title())
        rects.append(
            f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="{col}" rx="4"/>'
            f'<text x="{x + bar_w//2}" y="{y - 4}" text-anchor="middle" font-size="11" fill="#888">{score:.2f}</text>'
            f'<text x="{x + bar_w//2}" y="{H - 6}" text-anchor="middle" font-size="12" fill="#555">{label}</text>'
        )

    # Y-axis guide lines
    guides = "".join(
        f'<line x1="{pad_l}" y1="{pad_t + chart_h - int(chart_h*v)}" '
        f'x2="{W-pad_r}" y2="{pad_t + chart_h - int(chart_h*v)}" '
        f'stroke="#e5e7eb" stroke-width="0.5"/>'
        f'<text x="{pad_l-4}" y="{pad_t + chart_h - int(chart_h*v)+4}" '
        f'text-anchor="end" font-size="10" fill="#aaa">{v:.1f}</text>'
        for v in [0.25, 0.5, 0.75, 1.0]
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
        f'{guides}{"".join(rects)}'
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+chart_h}" stroke="#ccc" stroke-width="1"/>'
        f'<line x1="{pad_l}" y1="{pad_t+chart_h}" x2="{W-pad_r}" y2="{pad_t+chart_h}" stroke="#ccc" stroke-width="1"/>'
        f'</svg>'
    )


def _confusion_svg(m: EpisodeMetrics) -> str:
    """Render confusion matrix as an SVG heatmap."""
    if not m.confusion_matrix:
        return ""
    labels = m.confusion_matrix.labels
    matrix = m.confusion_matrix.matrix
    n      = len(labels)
    cell   = 64
    off    = 60
    W = H  = off + n * cell + 20

    cells_svg = []
    max_val   = max(
        matrix[t][p] for t in labels for p in labels
    ) or 1

    for ri, true in enumerate(labels):
        for ci, pred in enumerate(labels):
            val   = matrix[true][pred]
            alpha = 0.12 + 0.78 * (val / max_val)
            col   = f"rgba(34,197,94,{alpha:.2f})" if true == pred else f"rgba(239,68,68,{alpha:.2f})" if val > 0 else "#f9fafb"
            x, y  = off + ci * cell, off + ri * cell
            txt_c = "#fff" if alpha > 0.5 else "#333"
            cells_svg.append(
                f'<rect x="{x}" y="{y}" width="{cell-2}" height="{cell-2}" fill="{col}" rx="4"/>'
                f'<text x="{x+cell//2-1}" y="{y+cell//2+4}" text-anchor="middle" font-size="16" font-weight="600" fill="{txt_c}">{val}</text>'
            )

    headers = "".join(
        f'<text x="{off + i*cell + cell//2-1}" y="{off-8}" text-anchor="middle" font-size="11" fill="#666">P:{labels[i][:3]}</text>'
        f'<text x="{off-8}" y="{off + i*cell + cell//2+4}" text-anchor="end" font-size="11" fill="#666">T:{labels[i][:3]}</text>'
        for i in range(n)
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
        f'{headers}{"".join(cells_svg)}</svg>'
    )


# ── HTML template ──────────────────────────────────────────────────────────

def _score_badge(score: float) -> str:
    if   score >= 0.85: col, label = "#22c55e", "excellent"
    elif score >= 0.70: col, label = "#f59e0b", "good"
    elif score >= 0.50: col, label = "#f97316", "fair"
    else:               col, label = "#ef4444", "poor"
    return f'<span style="background:{col};color:#fff;padding:2px 8px;border-radius:999px;font-size:11px">{label}</span>'


def generate_report(agents_data: list[tuple], out_path: str = "report.html"):
    """
    agents_data: list of (EpisodeMetrics, list[step_dict])
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── per-agent sections ─────────────────────────────────────────────────
    agent_sections = []
    for m, steps in agents_data:
        bar_svg = _bar_chart_svg(m.per_difficulty)
        cm_svg  = _confusion_svg(m)

        # Per-class rows
        class_rows = "".join(
            f"<tr><td><b>{pc.label.upper()}</b></td>"
            f"<td>{pc.precision:.4f}</td><td>{pc.recall:.4f}</td>"
            f"<td>{pc.f1:.4f}</td><td>{pc.support}</td></tr>"
            for pc in (m.per_class or [])
        )

        # Step rows (cap at 100)
        def row_color(score):
            if score == 1.0: return "#f0fdf4"
            if score == 0.5: return "#fffbeb"
            return "#fef2f2"

        step_rows = "".join(
            f'<tr style="background:{row_color(s["score"])}">'
            f'<td>{s["email_id"]}</td>'
            f'<td style="font-size:12px">{html.escape(s["subject"][:60])}</td>'
            f'<td><span class="badge {s["difficulty"]}">{s["difficulty"]}</span></td>'
            f'<td><b>{s["predicted"].upper()}</b></td>'
            f'<td>{s["correct"].upper()}</td>'
            f'<td style="font-weight:600">{s["score"]}</td>'
            f'<td style="font-size:11px;color:#666">{html.escape(s["rationale"][:80])}</td>'
            f'</tr>'
            for s in steps
        )

        agent_sections.append(f"""
<section class="agent-section">
  <h2>{html.escape(m.agent_name)}</h2>

  <div class="card-row">
    <div class="card"><div class="card-label">Avg Score</div>
      <div class="card-value">{m.average_score:.4f}</div>{_score_badge(m.average_score)}</div>
    <div class="card"><div class="card-label">Accuracy</div>
      <div class="card-value">{m.accuracy:.4f}</div>{_score_badge(m.accuracy)}</div>
    <div class="card"><div class="card-label">Macro F1</div>
      <div class="card-value">{m.macro_f1:.4f}</div>{_score_badge(m.macro_f1)}</div>
    <div class="card"><div class="card-label">Weighted F1</div>
      <div class="card-value">{m.weighted_f1:.4f}</div>{_score_badge(m.weighted_f1)}</div>
    <div class="card"><div class="card-label">Correct</div>
      <div class="card-value g">{m.correct}</div></div>
    <div class="card"><div class="card-label">Partial</div>
      <div class="card-value y">{m.partial}</div></div>
    <div class="card"><div class="card-label">Incorrect</div>
      <div class="card-value r">{m.incorrect}</div></div>
  </div>

  <div class="two-col">
    <div>
      <h3>Score by Difficulty</h3>
      {bar_svg}
    </div>
    <div>
      <h3>Confusion Matrix</h3>
      {cm_svg}
    </div>
  </div>

  <h3>Per-Class Metrics</h3>
  <table>
    <tr><th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th></tr>
    {class_rows}
  </table>

  <h3>Step-by-Step Results</h3>
  <table>
    <tr><th>#</th><th>Subject</th><th>Difficulty</th>
        <th>Predicted</th><th>Correct</th><th>Score</th><th>Rationale</th></tr>
    {step_rows}
  </table>
</section>""")

    # ── Leaderboard ────────────────────────────────────────────────────────
    lb_rows = ""
    if len(agents_data) > 1:
        ranked = sorted(agents_data, key=lambda x: x[0].average_score, reverse=True)
        badges = ["🥇", "🥈", "🥉"]
        lb_rows = "".join(
            f"<tr><td>{badges[i] if i<3 else i+1}</td>"
            f"<td><b>{html.escape(m.agent_name)}</b></td>"
            f"<td>{m.average_score:.4f}</td><td>{m.accuracy:.4f}</td><td>{m.macro_f1:.4f}</td>"
            f"<td>{'—' if m.noise_delta is None else f'{m.noise_delta:+.4f}'}</td></tr>"
            for i, (m, _) in enumerate(ranked)
        )

    leaderboard_html = f"""
<section class="agent-section">
  <h2>Leaderboard</h2>
  <table>
    <tr><th>Rank</th><th>Agent</th><th>Avg Score</th><th>Accuracy</th><th>Macro F1</th><th>Noise Δ</th></tr>
    {lb_rows}
  </table>
</section>""" if lb_rows else ""

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email Sorting OpenEnv — Evaluation Report</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f8fafc; color: #1e293b; line-height: 1.6; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: .25rem; }}
  h2 {{ font-size: 1.3rem; font-weight: 600; margin: 2rem 0 1rem;
       padding-bottom: .5rem; border-bottom: 2px solid #e2e8f0; }}
  h3 {{ font-size: 1rem; font-weight: 600; margin: 1.5rem 0 .75rem; color: #475569; }}
  .meta {{ font-size: .85rem; color: #94a3b8; margin-bottom: 2rem; }}
  .agent-section {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
                    padding: 1.5rem; margin-bottom: 2rem; }}
  .card-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 1.5rem; }}
  .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
           padding: .75rem 1rem; min-width: 110px; }}
  .card-label {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing:.05em; }}
  .card-value {{ font-size: 1.4rem; font-weight: 700; line-height: 1.2; }}
  .card-value.g {{ color: #22c55e; }}
  .card-value.y {{ color: #f59e0b; }}
  .card-value.r {{ color: #ef4444; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .875rem; margin-bottom: 1rem; }}
  th {{ background: #f1f5f9; padding: 8px 12px; text-align: left;
        font-size: .8rem; letter-spacing: .04em; text-transform: uppercase; color: #64748b; }}
  td {{ padding: 7px 12px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  .badge {{ padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 500; }}
  .badge.easy   {{ background: #dcfce7; color: #166534; }}
  .badge.medium {{ background: #fef3c7; color: #92400e; }}
  .badge.hard   {{ background: #fee2e2; color: #991b1b; }}
  @media (max-width:700px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<h1>📧 Email Sorting OpenEnv</h1>
<p class="meta">Evaluation Report · Generated {now}</p>

{leaderboard_html}
{"".join(agent_sections)}
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"  Report saved → {os.path.abspath(out_path)}")
    return out_path


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate HTML evaluation report.")
    p.add_argument("--agent",  default=None, help="Specific agent name (default: all)")
    p.add_argument("--difficulty", default=None, choices=["easy","medium","hard"])
    p.add_argument("--out",    default="report.html")
    args = p.parse_args()

    agents = [cls() for cls in ALL_AGENTS]
    if args.agent:
        agents = [get_agent(args.agent)]

    print(f"\n  Running {len(agents)} agent(s)...")
    data = []
    for agent in agents:
        print(f"  → {agent.name}", end="", flush=True)
        m, steps = run_agent_detailed(agent, difficulty=args.difficulty)
        data.append((m, steps))
        print(f"  avg={m.average_score:.4f}  F1={m.macro_f1:.4f}")

    generate_report(data, out_path=args.out)