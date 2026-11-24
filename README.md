# Boreal Field Services

An AI-enabled field service architecture on SAP BTP and SAP S/4HANA, designed end to end: scenario, solution architecture, design decisions, and a working interactive prototype.

Boreal Field Services maintains ground support equipment for airports across the north. About 140 field engineers cover 22 stations, working on tablets in places where connectivity ranges from hangar Wi-Fi to satellite links to nothing at all for hours at a time. The design problem: a ground power unit fails its start check on a January morning, a medevac flight is due through the station in five hours, and the part the system says is on the shelf is not there, because another crew consumed it yesterday and their tablet has not synced since.

## The design in one line

Events wake the agents, context tells them what things mean, guardrails decide what they are allowed to do, and a human owns the commitments.

## The architecture

Every layer has one job. No layer does another layer's job.

- **The field (tablets):** the capture application records findings, time, parts used and customer sign-off, online or offline. Capture is a side-by-side extension, not an agent, because it has to be deterministic and available with no connection.
- **Identity:** SAP Cloud Identity Services. The tablet acts as the person signed in, never as "a tablet."
- **Joule Studio:** where the three agents, Scout (issue triage), Stock (availability and options) and Dispatch (schedule and impact), are built and run. Judgement work only.
- **AI Core / GenAI Hub:** the model runtime underneath the agents.
- **Business Data Cloud and the Knowledge Graph:** the shared meaning. A part carries what it is reserved for; an engineer carries their certifications; a module carries the contract that depends on it. Context lives in the platform, not inside any agent.
- **Integration Suite:** the only road in. APIs for deliberate lookups, events for change, store-and-forward sync for the tablets.
- **SAP S/4HANA:** the system of record. Work orders, inventory, contracts, billing. Kept clean so it can be upgraded.
- **AI Agent Hub and governance:** every agent registered with a named owner, offline authority bounded in the application, sync conflicts resolved by humans with the evidence attached, human approval for consequential actions.

Key principles the design holds:

- The agent cannot turn stale data into confirmed stock.
- The agent cannot turn an uncertain recovery plan into a customer commitment.
- The application executes transactions; agents investigate and recommend.
- Human approval for consequential actions.

## Contents

- `prototype/index.html` — the interactive prototype. Open it in a browser and run the January morning yourself: step through the event, watch the three agents work, and try both approvals at the gate. The unverified transfer is refused; the verified one goes through.
- `docs/boreal-field-services-scenario.md` — the full scenario: the company, the January event, the three pillars (Build, Contextualize and Reason, Govern), the end-to-end sequence, and the five design calls with the alternatives rejected.
- `docs/design-decisions-and-follow-up-answers.md` — the design decisions defended in depth, including the feedback loop and where Joule Studio sits.
- `docs/boreal-complete-package-2026-11-20.pdf` — the complete package as a single document.
- `images/` — the design sheets the prototype was built and checked against: the overall solution architecture, the end-to-end architecture arc, the handwritten solution architecture view, and the design in one picture.

## Status

Design and interactive prototype. All data is synthetic: no real company, system or operational data, and no live connection to any SAP system. The prototype is a simulation that demonstrates the architecture and its guardrails.

Designed by Anahita Jacobsen.
