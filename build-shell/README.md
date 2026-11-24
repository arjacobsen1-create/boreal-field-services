# Boreal Field Services — Build Shell

**What this is:** a project skeleton (shell only) for the Boreal Field Services
architecture. It is a display/simulation scaffold — **NOT connected to any real
S/4HANA or SAP system**, no live integrations, and all data is **100% synthetic**.
Nothing here is published or deployed.

Built faithfully from the Boreal Field Services Solution Architecture diagram
(handwritten view): AI-enabled field service for aerospace MRO, SAP BTP + SAP S/4HANA.

## Scenario it carries

Engineer Dana, at a remote home station in severe winter cold, faces a failed ground power
unit five hours before a medevac flight. The failed part is a voltage regulator
module. S/4HANA shows one on the home-station shelf — phantom stock (consumed
yesterday by a crew whose tablet had not synced). Station B holds a verified
unit; Station C shows a unit that is unverified (not synced in 26 hours).

## Layer map — folder ↔ diagram box

| Folder | Diagram box | Job |
|---|---|---|
| `app/` | Field Service Application (CAP), in SAP BTP — Application & Extension Layer | APIs, offline sync & validation, conflict handling, business rules |
| `agents/` | Joule Studio — AI Agents (Scout, Stock, Dispatch) | Investigate and recommend; never execute transactions |
| `ai/` | AI Core / GenAI Hub | Managed AI runtime, model access, Responsible AI controls (Python lives here) |
| `integration/` | Integration & Context Services | Integration Suite (APIs, events), Business Data Cloud (governed data), Knowledge Graph (business relationships) |
| `data/` | Synthetic stand-in for S/4HANA — System of Record | Work orders, inventory & reservations, equipment, contracts/SLAs, billing (simulated only) |
| `governance/` | Cross-Cutting Governance & Operations | Agent Hub, monitoring & audit, data quality, model governance & guardrails, device security |
| (diagram, left) | Identity & Access — SAP Cloud Identity Services | Authentication, authorisation (roles), conditional access on managed tablets. Noted here; no folder in this shell |

Field Engineers — Tablets (Dana + team) sit at the top of the diagram: work
orders, parts usage, photos/notes, offline (encrypted), sync queue when in
coverage. The tablet client is not stubbed in this shell.

## Language placement (design decision)

- **Application layer (CAP): Java or Node.js.** There is no Python CAP.
- **AI layer: Python** (AI Core / GenAI Hub side).
- **Agents: configured, not coded** (Joule Studio).

## Key principles (from the diagram)

- The agent cannot turn stale data into confirmed stock.
- The agent cannot turn an uncertain recovery plan into a customer commitment.
- Agents use governed data (BDC) with business context (Knowledge Graph).
- The application executes transactions; agents investigate and recommend.
- Human approval for consequential actions.
