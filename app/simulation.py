"""Boreal Field Services - the morning as a Python state machine.

This is the prototype, recreated in Python: the same January morning,
the same three agents, the same gate, implemented as a state machine
the dashboard renders. The eight steps are the "From Event to Outcome"
flow from the design's Overall Solution Architecture sheet:

  1  Engineer records a part shortage on the tablet (offline).
  2  App validates and syncs when in coverage.
  3  Integration updates S/4HANA.
  4  Stock agent investigates using BDC + Knowledge Graph.
  5  Agent proposes options (transfer, expedite, reschedule).
  6  Human approves the action.            <- the gate lives here
  7  Execution updates S/4HANA.
  8  Outcome: issue resolved, customer informed, audit trail.

The run advances freely through steps 1 to 5. It will not cross step 6
on its own: a transfer must be put to the gate, and the gate's rules
(gates.py) decide. The unverified Station C transfer is refused and
logged, and the morning stays at the gate. The verified Station B
transfer, approved by a named human, completes steps 6 to 8.

Stdlib only. All data is synthetic (data/sample-stock.json).
"""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from .gates import AuditLog, Gate
    from .stock_picture import StockPicture, load_stock_picture
except ImportError:  # running as loose scripts inside the folder
    from gates import AuditLog, Gate
    from stock_picture import StockPicture, load_stock_picture

SUPERVISOR = "A. Lindqvist, Station Supervisor"

STEPS = [
    ("Capture", "Engineer records a part shortage on the tablet (offline).",
     "Stored locally (encrypted) and queued for sync."),
    ("Capture", "App validates and syncs when in coverage.",
     "CAP services check data, resolve conflicts."),
    ("Reason", "Integration updates S/4HANA.",
     "Work order and inventory are updated."),
    ("Reason", "Stock agent investigates using BDC + Knowledge Graph.",
     "Finds related parts, suppliers, impact."),
    ("Decide", "Agent proposes options (transfer, expedite, reschedule).",
     "Shows facts and uncertainty. No execution."),
    ("Decide", "Human approves the action.",
     "Via workflow and approval controls."),
    ("Execute", "Execution updates S/4HANA.",
     "Transaction goes through the business process."),
    ("Learn", "Outcome: issue resolved, customer informed, audit trail.",
     "Full traceability and monitoring."),
]

ARC = ["Capture", "Reason", "Decide", "Execute", "Learn"]

AGENTS = {
    "Scout": ("Issue triage",
              "Assembles the job pack: work order, service history, "
              "manual sections, and an honest parts picture."),
    "Stock": ("Availability & options",
              "Watches stock across all 22 station stores, sees "
              "reservations and priorities, proposes transfers."),
    "Dispatch": ("Schedule & impact",
                 "Assigns and re-sequences jobs around engineer "
                 "location, certifications, and the medevac clock."),
}

# What each agent is doing at each step (index 0 = before the run starts).
AGENT_ACTIVITY = {
    "Scout": [
        "Waiting with the tablet at the hangar.",
        "Records the shortage offline and queues it for sync.",
        "Sync lands; the pack is validated.",
        "Pack handed to the platform; history attached.",
        "Watches Stock's investigation; pack stays open.",
        "Presents the options with the pack's evidence.",
        "Stands by while the human decides.",
        "Records the outcome against the work order.",
        "Closes the pack; the trail is complete.",
    ],
    "Stock": [
        "Watching stock across 22 stations.",
        "Idle: the event has not reached the platform yet.",
        "Idle: sync in transit.",
        "Wakes on the inventory update.",
        "Investigates via BDC + Knowledge Graph: home line is a "
        "phantom, Station C unverified, Station B confirmed.",
        "Proposes the Station B transfer; flags Station C as "
        "unverified and not a safe option.",
        "Waits at the gate for the human decision.",
        "Executes the approved transfer through integration.",
        "Confirms the part is moving; stock picture updated.",
    ],
    "Dispatch": [
        "Watching the 10:15 medevac deadline.",
        "Notes the failed start check against the deadline.",
        "Holds the schedule while data syncs.",
        "Re-sequences around the work order.",
        "Checks both transfer ETAs against the deadline.",
        "Confirms Station B's 40 minutes fits the deadline.",
        "Waits at the gate; no customer promise made.",
        "Informs the customer once execution is confirmed.",
        "Morning resolved with time to spare.",
    ],
}


@dataclass
class Morning:
    """One run of the January morning."""

    picture: StockPicture = field(default_factory=load_stock_picture)
    audit: AuditLog = field(default_factory=AuditLog)
    step: int = 0  # steps completed, 0..8
    resolved: bool = False
    gate_note: str = ""

    def __post_init__(self) -> None:
        self.gate = Gate(self.audit)

    @property
    def at_gate(self) -> bool:
        return self.step == 5 and not self.resolved

    @property
    def arc_stage(self) -> str | None:
        if self.step == 0:
            return None
        return STEPS[self.step - 1][0] if self.step <= 7 else "Learn"

    def agent_status(self, name: str) -> tuple[str, str]:
        activity = AGENT_ACTIVITY[name][self.step]
        if self.resolved:
            state = "DONE"
        elif self.step == 0:
            state = "IDLE"
        else:
            state = "WORKING"
        return state, activity

    def advance(self) -> str:
        """Move one step. The gate step cannot be crossed by advancing."""
        if self.resolved:
            return "The morning is already resolved."
        if self.at_gate:
            self.gate_note = (
                "GATE HOLD: step 6 is the human decision. Choose a "
                "transfer to approve; the gate will rule on it."
            )
            return self.gate_note
        if self.step < 5 or self.step >= 6:
            self.step = min(self.step + 1, 8)
            self.gate_note = ""
            return f"Advanced to step {self.step} of 8."
        return self.gate_note

    def approve(self, station: str, approver: str | None = SUPERVISOR) -> str:
        """Put a transfer to the gate. Only meaningful at the gate."""
        if not self.at_gate:
            self.gate_note = "The gate is step 6. Run the morning to step 5 first."
            return self.gate_note
        line = self.picture.line_for(station)
        decision = self.gate.evaluate_transfer("Stock", line, approver)
        if not decision.approved:
            self.gate_note = f"GATE REFUSAL: {decision.reason}"
            return self.gate_note
        # Approved: the human decision (6), execution (7), outcome (8).
        self.step = 8
        self.resolved = True
        commitment = self.gate.evaluate_customer_commitment(
            "Dispatch", plan_depends_on=[line], approver=approver
        )
        self.gate_note = (
            f"APPROVED: {decision.reason} Execution updated S/4HANA; "
            f"customer commitment {'issued' if commitment.approved else 'refused'}."
        )
        return self.gate_note

    def reset(self) -> None:
        self.picture = load_stock_picture()
        self.audit = AuditLog()
        self.gate = Gate(self.audit)
        self.step = 0
        self.resolved = False
        self.gate_note = ""
