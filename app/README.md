# Boreal Field Services - the Python implementation

The prototype, recreated in Python: the same January morning, the same
three agents, the same gate, implemented as a Python application rather
than a static page. This is the main implementation. The static HTML
version under `../prototype/` is the mirror served on GitHub Pages.

## Run the dashboard

```bash
python3 -m app.serve        # from the repository root
```

Then open http://localhost:8000. Run the morning with the step button,
and try both approvals at the gate: the unverified Station C transfer
is refused and logged; the verified Station B transfer resolves the
morning. Standard library only, nothing to install.

## How it is put together

Every layer has one job, in code as in the architecture:

- `simulation.py` — the morning as a state machine. The eight steps
  are the design's "From Event to Outcome" flow. The run advances
  through steps 1 to 5 and stops at the gate: step 6 is the human
  decision and cannot be crossed by advancing.
- `stock_picture.py` — what counts as stock. Classifies every line in
  `data/sample-stock.json` as confirmed, phantom, or unverified. Only
  confirmed stock may be planned against.
- `gates.py` — the governance rules from the design's gates.yaml as
  enforced code: no approval on unverified stock, a named human
  approver for consequential actions, no customer commitment on an
  uncertain plan, every refusal written to the audit log.
- `dashboard.py` — the page, rendered from the simulation state:
  agent cards with live status, the arc, the steps, the stock picture,
  the gate, and the audit log.
- `serve.py` — a standard-library web server. Routes: `/step`,
  `/approve-b`, `/approve-c`, `/reset`.

## Test it

```bash
python3 -m app.test_gates        # the governance rules, 7 checks
python3 -m app.test_simulation   # the run and the gate, 5 checks
```

All data is synthetic. No real system is connected.
