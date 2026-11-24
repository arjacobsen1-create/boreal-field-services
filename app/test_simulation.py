"""Boreal Field Services - simulation tests.

    python3 -m app.test_simulation     (from the repository root)
    python3 test_simulation.py         (from inside app/)

Pins the behaviour of the Python recreation: the run cannot cross the
gate on its own, the unverified transfer is refused and the morning
stays at the gate, the verified transfer resolves the morning, and a
gate attempt before step 6 changes nothing.
"""

from __future__ import annotations

try:
    from .simulation import Morning
except ImportError:  # running as loose scripts inside the folder
    from simulation import Morning


def run_to_gate(morning: Morning) -> None:
    for _ in range(5):
        morning.advance()
    assert morning.step == 5 and morning.at_gate


def test_gate_cannot_be_crossed_by_advancing() -> None:
    morning = Morning()
    run_to_gate(morning)
    morning.advance()
    assert morning.step == 5 and not morning.resolved
    assert "GATE HOLD" in morning.gate_note


def test_unverified_refused_and_morning_stays() -> None:
    morning = Morning()
    run_to_gate(morning)
    morning.approve("Station C")
    assert not morning.resolved and morning.step == 5
    assert "GATE REFUSAL" in morning.gate_note
    assert len(morning.audit.refusals()) == 1


def test_verified_approval_resolves() -> None:
    morning = Morning()
    run_to_gate(morning)
    morning.approve("Station B")
    assert morning.resolved and morning.step == 8
    kinds = [entry.kind for entry in morning.audit.entries]
    assert kinds == ["approval", "approval"]  # transfer, then commitment


def test_gate_attempt_too_early_changes_nothing() -> None:
    morning = Morning()
    morning.approve("Station B")
    assert morning.step == 0 and not morning.resolved
    assert morning.audit.entries == []


def test_reset_restores_the_morning() -> None:
    morning = Morning()
    run_to_gate(morning)
    morning.approve("Station B")
    morning.reset()
    assert morning.step == 0 and not morning.resolved
    assert morning.audit.entries == []


if __name__ == "__main__":
    tests = [
        test_gate_cannot_be_crossed_by_advancing,
        test_unverified_refused_and_morning_stays,
        test_verified_approval_resolves,
        test_gate_attempt_too_early_changes_nothing,
        test_reset_restores_the_morning,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\nAll {len(tests)} simulation tests passed.")
