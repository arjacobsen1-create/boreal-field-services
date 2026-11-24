"""Boreal Field Services - the governance gates, as enforced code.

These are the rules from governance/gates.yaml, implemented rather than
described. The agents propose; the gates decide what may proceed; a human
owns every consequential commitment.

Rules implemented:
  no-approval-on-unverified-stock
      Approval never applies to a stock line whose status is unverified.
      A phantom line is refused on the same ground: it is not stock.
  human-approval-for-consequential-actions
      Reservations, transfers and customer commitments require a named
      human approver. An agent's own say-so is never an approval.
  no-customer-commitment-on-uncertain-plan
      No customer commitment may be issued while the recovery plan
      depends on unverified stock or unconfirmed ETAs.
  every-refusal-logged
      Every refusal is written to the audit log with the agent, the
      line, the rule id and the reason. Approvals are logged too.

Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from stock_picture import CONFIRMED, PHANTOM, UNVERIFIED, StockLine

RULE_NO_APPROVAL_ON_UNVERIFIED = "no-approval-on-unverified-stock"
RULE_HUMAN_APPROVAL = "human-approval-for-consequential-actions"
RULE_NO_COMMITMENT_ON_UNCERTAIN_PLAN = "no-customer-commitment-on-uncertain-plan"
RULE_EVERY_REFUSAL_LOGGED = "every-refusal-logged"


@dataclass
class AuditEntry:
    kind: str  # "approval" or "refusal"
    agent: str
    subject: str
    rule_id: str | None
    reason: str

    def __str__(self) -> str:
        rule = f" [{self.rule_id}]" if self.rule_id else ""
        return f"{self.kind.upper()}{rule} {self.subject} - {self.reason}"


@dataclass
class AuditLog:
    entries: list[AuditEntry] = field(default_factory=list)

    def record(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def refusals(self) -> list[AuditEntry]:
        return [e for e in self.entries if e.kind == "refusal"]

    def render(self) -> str:
        return "\n".join(f"  {entry}" for entry in self.entries)


@dataclass
class Decision:
    approved: bool
    rule_id: str | None
    reason: str


class Gate:
    """Evaluates proposed actions against the governance rules."""

    def __init__(self, audit_log: AuditLog):
        self.audit = audit_log

    def _refuse(self, agent: str, subject: str, rule_id: str, reason: str) -> Decision:
        self.audit.record(AuditEntry("refusal", agent, subject, rule_id, reason))
        return Decision(approved=False, rule_id=rule_id, reason=reason)

    def evaluate_transfer(
        self, agent: str, line: StockLine, approver: str | None
    ) -> Decision:
        """May `agent` reserve and transfer the part held on `line`?

        The stock rules are checked before the human rule on purpose:
        no approver, however senior, can approve stock that is not
        confirmed. The gate cannot turn stale data into confirmed stock.
        """
        subject = f"transfer of part from {line.station} (proposed by {agent})"

        if line.classification == PHANTOM:
            return self._refuse(
                agent,
                subject,
                RULE_NO_APPROVAL_ON_UNVERIFIED,
                "Phantom stock: the system shows "
                f"{line.system_shows} but the physical count is {line.actual}. "
                "There is nothing to transfer.",
            )
        if line.classification == UNVERIFIED:
            return self._refuse(
                agent,
                subject,
                RULE_NO_APPROVAL_ON_UNVERIFIED,
                f"Stock at {line.station} is unverified "
                f"(last sync: {line.last_sync}). Approval never applies "
                "to an unverified stock line.",
            )
        if not approver:
            return self._refuse(
                agent,
                subject,
                RULE_HUMAN_APPROVAL,
                "Consequential actions require a named human approver. "
                "Agents propose; humans approve.",
            )

        reason = (
            f"Confirmed stock at {line.station} "
            f"(last sync: {line.last_sync}); approved by {approver}."
        )
        self.audit.record(
            AuditEntry("approval", agent, subject, None, reason)
        )
        return Decision(approved=True, rule_id=None, reason=reason)

    def evaluate_customer_commitment(
        self, agent: str, plan_depends_on: list[StockLine], approver: str | None
    ) -> Decision:
        """May `agent` commit this plan to the customer?

        The gate cannot turn an uncertain recovery plan into a customer
        commitment: if any line the plan depends on is not confirmed,
        the commitment is refused, whoever asks.
        """
        subject = f"customer commitment (proposed by {agent})"
        uncertain = [
            line.station
            for line in plan_depends_on
            if line.classification != CONFIRMED
        ]
        if uncertain:
            return self._refuse(
                agent,
                subject,
                RULE_NO_COMMITMENT_ON_UNCERTAIN_PLAN,
                "The plan depends on unconfirmed stock at "
                + ", ".join(uncertain)
                + ". No customer commitment on an uncertain plan.",
            )
        if not approver:
            return self._refuse(
                agent,
                subject,
                RULE_HUMAN_APPROVAL,
                "A customer commitment requires a named human approver.",
            )
        reason = f"Plan rests on confirmed stock only; approved by {approver}."
        self.audit.record(AuditEntry("approval", agent, subject, None, reason))
        return Decision(approved=True, rule_id=None, reason=reason)
