"""Boreal Field Services - the dashboard, rendered by Python.

The page is generated from the simulation state (simulation.Morning):
agent cards with live status, the five-stage arc, the eight steps,
the stock picture, the gate, and the audit log. Styling follows the
settled look of the design: solid off-white page, white cards, dark
purple text, light scheme in every mode.
"""

from __future__ import annotations

import html

try:
    from .simulation import AGENTS, ARC, STEPS, Morning
except ImportError:  # running as loose scripts inside the folder
    from simulation import AGENTS, ARC, STEPS, Morning

CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #fbf9ff; color: #2e1065;
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif; }
main { max-width: 1060px; margin: 0 auto; padding: 24px 18px 48px; }
h1 { font-size: 30px; margin: 0 0 4px; }
h2 { font-size: 20px; margin: 28px 0 10px; color: #4c1d95; }
.sub { color: #5b21b6; margin: 0 0 14px; }
.bar { position: sticky; top: 0; background: #fbf9ff; padding: 10px 0;
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
  border-bottom: 2px solid #ddd6fe; z-index: 5; }
button { font: inherit; cursor: pointer; border-radius: 10px;
  border: 2px solid #7c3aed; padding: 8px 16px; font-weight: 600; }
.run { background: #7c3aed; color: #fff; }
.ghost { background: #fff; color: #4c1d95; }
.good { background: #db2777; border-color: #db2777; color: #fff; }
.counter { font-weight: 700; color: #4c1d95; }
.note { background: #fdf2f8; border: 2px solid #f9a8d4; color: #831843;
  border-radius: 12px; padding: 10px 14px; margin: 12px 0; }
.panel { background: #f3efff; border: 2px solid #c4b5fd;
  border-radius: 16px; padding: 14px; }
.grid { display: grid; gap: 12px; grid-template-columns: repeat(3, 1fr); }
@media (max-width: 760px) { .grid { grid-template-columns: 1fr; } }
.card { background: #fff; border: 2px solid #c4b5fd; border-radius: 14px;
  padding: 14px; }
.card h3 { margin: 0 0 2px; font-size: 19px; }
.role { color: #7c3aed; font-weight: 700; margin: 0 0 8px; }
.pill { display: inline-block; background: #ede9fe; color: #5b21b6;
  border-radius: 999px; padding: 2px 10px; font-size: 12px;
  font-weight: 800; letter-spacing: .06em; }
.pill.working { background: #7c3aed; color: #fff; }
.pill.done { background: #059669; color: #fff; }
.arc { display: grid; gap: 10px; grid-template-columns: repeat(5, 1fr); }
@media (max-width: 760px) { .arc { grid-template-columns: repeat(2, 1fr); } }
.stage { background: #fff; border: 2px solid #c4b5fd; border-radius: 12px;
  padding: 10px; opacity: .55; }
.stage.lit { opacity: 1; border-color: #7c3aed; background: #ede9fe; }
ol.steps li { margin: 6px 0; }
ol.steps li.done { color: #4c1d95; font-weight: 600; }
ol.steps li.now { background: #ede9fe; border-radius: 8px; padding: 4px 8px; }
table { border-collapse: collapse; width: 100%; background: #fff; }
th, td { border: 1px solid #ddd6fe; padding: 8px 10px; text-align: left; }
th { background: #ede9fe; }
.log { background: #fff; border: 2px solid #c4b5fd; border-radius: 12px;
  padding: 12px 16px; font-family: ui-monospace, monospace; font-size: 14px;
  white-space: pre-wrap; }
footer { color: #5b21b6; font-size: 14px; margin-top: 28px; }
"""


def _agent_cards(morning: Morning) -> str:
    cards = []
    for name, (role, _desc) in AGENTS.items():
        state, activity = morning.agent_status(name)
        cards.append(
            f'<div class="card"><h3>{html.escape(name)}</h3>'
            f'<p class="role">{html.escape(role)}</p>'
            f'<span class="pill {state.lower()}">{state}</span>'
            f"<p>{html.escape(activity)}</p></div>"
        )
    return "\n".join(cards)


def _arc(morning: Morning) -> str:
    lit = ARC.index(morning.arc_stage) if morning.arc_stage else -1
    boxes = []
    for i, stage in enumerate(ARC):
        cls = "stage lit" if i <= lit else "stage"
        boxes.append(f'<div class="{cls}"><strong>{i + 1} {stage}</strong></div>')
    return "\n".join(boxes)


def _steps(morning: Morning) -> str:
    items = []
    for i, (_stage, title, detail) in enumerate(STEPS, start=1):
        cls = "done" if i <= morning.step else ("now" if i == morning.step + 1 else "")
        items.append(
            f'<li class="{cls}"><strong>{html.escape(title)}</strong> '
            f"{html.escape(detail)}</li>"
        )
    return "\n".join(items)


def _stock_table(morning: Morning) -> str:
    rows = []
    for line in morning.picture.lines:
        rows.append(
            "<tr>"
            f"<td>{html.escape(line.station)}</td>"
            f"<td>{line.system_shows}</td>"
            f"<td>{'unknown' if line.actual is None else line.actual}</td>"
            f"<td>{html.escape(line.classification)}</td>"
            f"<td>{html.escape(line.last_sync or 'not recorded')}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render(morning: Morning) -> str:
    note = (
        f'<div class="note">{html.escape(morning.gate_note)}</div>'
        if morning.gate_note
        else ""
    )
    log_text = morning.audit.render() or "No decisions yet. The log fills as the gate rules."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>Boreal Field Services - Solution Architecture</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>Boreal Field Services</h1>
<p class="sub">AI-enabled field service for aerospace MRO (SAP BTP + SAP S/4HANA).
The January morning, running in Python. Display / simulation only: 100% synthetic
data, no real connection to any SAP system.</p>

<div class="bar">
  <form method="post" action="/step"><button class="run" type="submit">Run next step</button></form>
  <form method="post" action="/reset"><button class="ghost" type="submit">Reset</button></form>
  <span class="counter">Step {morning.step} of 8{" - RESOLVED" if morning.resolved else ""}</span>
</div>
{note}

<h2>The three agents</h2>
<div class="panel"><div class="grid">
{_agent_cards(morning)}
</div></div>

<h2>The end-to-end arc</h2>
<div class="arc">
{_arc(morning)}
</div>

<h2>From Event to Outcome</h2>
<ol class="steps">
{_steps(morning)}
</ol>

<h2>The gate (step 6)</h2>
<p>Approval never applies to unverified stock, and consequential actions need a
named human approver. Try both transfers when the run reaches the gate:</p>
<form method="post" action="/approve-c" style="display:inline">
  <button class="ghost" type="submit">Approve Station C transfer (unverified)</button></form>
<form method="post" action="/approve-b" style="display:inline">
  <button class="good" type="submit">Approve Station B transfer (verified)</button></form>

<h2>The stock picture</h2>
<table>
<tr><th>Station</th><th>System shows</th><th>Actual</th><th>Classification</th><th>Last sync</th></tr>
{_stock_table(morning)}
</table>

<h2>Audit log</h2>
<div class="log">{html.escape(log_text)}</div>

<footer>Agents investigate and recommend. They don't execute consequential
actions. S/4HANA remains the authoritative system for transactions.</footer>
</main>
</body>
</html>"""
