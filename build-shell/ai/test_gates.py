"""Boreal Field Services - gate behaviour tests.

Plain asserts, no test framework needed:

    python3 test_gates.py

Each test pins one governance rule from governance/gates.yaml to the
behaviour the design promises. If a rule ever stops holding, a test
here fails before a customer finds out.
"""

from __future__ import annotations

from gates import (
    RULE_HUMAN_APPROVAL,
    RULE_NO_APPROVAL_ON_UNVERIFIED,
    RULE_NO_COMMITMENT_ON_UNCERTAIN_PLAN,
    AuditLog,
    Gate,
)
from stock_picture import CONFIRMED, PHANTOM, UNVERIFIED, load_stock_picture

SUPERVISOR = "A. Lindqvist, Station Supervisor"


def fresh_gate() -> tuple[Gate, AuditLog]:
    audit = AuditLog()
    return Gate(audit), audit


def test_stock_classification() -> None:
    picture = load_stock_picture()
    assert picture.line_for("Home Station").classification == PHANTOM
    assert picture.line_for("Station B").classification == CONFIRMED
    assert picture.line_for("Station C").classification == UNVERIFIED
    # Only confirmed stock may be planned against.
    assert picture.line_for("Home Station").available == 0
    assert picture.line_for("Station C").available == 0
    assert picture.line_for("Station B").available == 1


def test_phantom_transfer_refused() -> None:
    gate, _ = fresh_gate()
    home = load_stock_picture().line_for("Home Station")
    decision = gate.evaluate_transfer("Stock", home, approver=SUPERVISOR)
    assert not decision.approved
    assert decision.rule_id == RULE_NO_APPROVAL_ON_UNVERIFIED


def test_unverified_transfer_refused_even_with_approver() -> None:
    gate, _ = fresh_gate()
    station_c = load_stock_picture().line_for("Station C")
    decision = gate.evaluate_transfer("Stock", station_c, approver=SUPERVISOR)
    assert not decision.approved
    assert decision.rule_id == RULE_NO_APPROVAL_ON_UNVERIFIED


def test_verified_transfer_needs_a_human() -> None:
    gate, _ = fresh_gate()
    station_b = load_stock_picture().line_for("Station B")
    decision = gate.evaluate_transfer("Stock", station_b, approver=None)
    assert not decision.approved
    assert decision.rule_id == RULE_HUMAN_APPROVAL


def test_verified_transfer_approved_with_human() -> None:
    gate, _ = fresh_gate()
    station_b = load_stock_picture().line_for("Station B")
    decision = gate.evaluate_transfer("Stock", station_b, approver=SUPERVISOR)
    assert decision.approved


def test_no_commitment_on_uncertain_plan() -> None:
    gate, _ = fresh_gate()
    picture = load_stock_picture()
    decision = gate.evaluate_customer_commitment(
        "Dispatch",
        plan_depends_on=[picture.line_for("Station C")],
        approver=SUPERVISOR,
    )
    assert not decision.approved
    assert decision.rule_id == RULE_NO_COMMITMENT_ON_UNCERTAIN_PLAN


def test_every_refusal_is_logged() -> None:
    gate, audit = fresh_gate()
    picture = load_stock_picture()
    gate.evaluate_transfer("Stock", picture.line_for("Station C"), SUPERVISOR)
    gate.evaluate_transfer("Stock", picture.line_for("Station B"), None)
    refusals = audit.refusals()
    assert len(refusals) == 2
    assert all(entry.rule_id for entry in refusals)
    assert all(entry.agent == "Stock" for entry in refusals)


if __name__ == "__main__":
    tests = [
        test_stock_classification,
        test_phantom_transfer_refused,
        test_unverified_transfer_refused_even_with_approver,
        test_verified_transfer_needs_a_human,
        test_verified_transfer_approved_with_human,
        test_no_commitment_on_uncertain_plan,
        test_every_refusal_is_logged,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\nAll {len(tests)} gate tests passed.")
