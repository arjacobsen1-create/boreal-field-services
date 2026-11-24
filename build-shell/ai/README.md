# The AI layer (Python)

Where Python lives in the Boreal architecture: the agents' decision
logic, under the Joule Studio agents and beside AI Core / GenAI Hub.
The CAP application layer is Java or Node.js; the agents themselves are
configured in Joule Studio; the logic that decides what the agents may
propose, and what the gates allow, is written here.

## What is implemented

- `stock_picture.py` — what counts as stock. Loads the stock picture
  and classifies every line: confirmed, phantom (system quantity
  disagrees with the physical count), or unverified (station has not
  synced). Only confirmed stock may be planned against.
- `gates.py` — the governance rules from `../governance/gates.yaml` as
  enforced code: no approval on unverified stock, a named human
  approver for consequential actions, no customer commitment on an
  uncertain plan, and every refusal written to the audit log.
- `run_morning.py` — the January morning, end to end: Scout's pack,
  Stock's investigation, the Station C refusal, the Station B approval,
  Dispatch's commitment check, and the audit trail.
- `test_gates.py` — the rules pinned as tests. Seven checks, plain
  asserts, no framework.
- `model_access.py` — the one deliberate placeholder: live model calls
  through AI Core / GenAI Hub belong to the real build. The decision
  logic above is deterministic and does not depend on a model.

## Run it

```bash
cd build-shell/ai
python3 run_morning.py
python3 test_gates.py
```

Standard library only. Data is the synthetic stock picture in
`../data/sample-stock.json`. No real system is connected.
