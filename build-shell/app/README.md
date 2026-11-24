# app/ — Field Service Application (CAP shell)

SAP BTP — Application & Extension Layer. Stub only; no runtime, no deployment.

## Language choice

CAP is implemented in **Java (Spring) or Node.js**. There is **no Python CAP** —
Python lives in the AI layer (`../ai/`). Pick one stack when the real build
starts, based on team skills; the data model and rules below are stack-neutral.

## What this layer owns

- APIs for the tablet clients and the agent layer
- Offline sync & validation of records captured on tablets (encrypted at rest)
- Conflict handling when syncs disagree (e.g. two crews, one part)
- Business rules (authorisation per station/role, reservation rules)

## Files

- `model.cds` — CDS-style data-model stub: WorkOrder, PartUsage,
  StockReservation, plus sync/validation/conflict rules as comments.
