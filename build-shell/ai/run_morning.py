"""Boreal Field Services - run the January morning.

A runnable simulation of the scenario in docs/boreal-field-services-scenario.md,
using the synthetic stock picture in data/sample-stock.json and the gate
rules in governance/gates.yaml (implemented in gates.py).

    python3 run_morning.py

The morning, in the design's own sequence: the ground power unit fails
its start check; Scout builds the job pack and finds the home-station
line cannot be trusted; Stock investigates the alternatives through the
stock picture; the tempting transfer (Station C, closer, unverified) is
put to the gate and refused; the verified transfer (Station B) is
approved by a named human; Dispatch checks the ETA against the medevac
deadline; and everything leaves an audit trail.

Display / simulation only. No real system is connected.
"""

from __future__ import annotations

from gates import AuditLog, Gate
from stock_picture import CONFIRMED, PHANTOM, UNVERIFIED, load_stock_picture

SUPERVISOR = "A. Lindqvist, Station Supervisor"


def main() -> None:
    picture = load_stock_picture()
    audit = AuditLog()
    gate = Gate(audit)

    req = picture.required_by
    print("05:10  Ground power unit fails its start check.")
    print(
        f"       Work order {req['workOrder']}: {req['equipment']}, "
        f"engineer {req['engineer']}, deadline {req['deadline']}."
    )
    print(f"       Part needed: {picture.part}.\n")

    print("Scout builds the job pack and reads the stock picture:")
    print(picture.summary())
    home = picture.line_for("Home Station")
    print(
        f"\n       The home line is a phantom: {home.detail}\n"
        "       The pack therefore plans a transfer as the primary path.\n"
    )

    station_c = picture.line_for("Station C")
    station_b = picture.line_for("Station B")

    print(
        f"Stock investigates. Station C is closer "
        f"(ETA {station_c.transfer_eta}) but unverified "
        f"(last sync {station_c.last_sync}). Stock proposes it anyway,\n"
        "       to test the gate:"
    )
    decision = gate.evaluate_transfer("Stock", station_c, approver=SUPERVISOR)
    print(f"       Gate: {'APPROVED' if decision.approved else 'REFUSED'} - {decision.reason}\n")

    print(
        f"Stock proposes Station B (ETA {station_b.transfer_eta}, "
        f"last sync {station_b.last_sync}):"
    )
    decision = gate.evaluate_transfer("Stock", station_b, approver=SUPERVISOR)
    print(f"       Gate: {'APPROVED' if decision.approved else 'REFUSED'} - {decision.reason}\n")

    print(
        "Dispatch checks the plan against the deadline: transfer ETA "
        f"{station_b.transfer_eta} against the {req['deadline']} deadline."
    )
    commitment = gate.evaluate_customer_commitment(
        "Dispatch", plan_depends_on=[station_b], approver=SUPERVISOR
    )
    print(
        f"       Customer commitment: "
        f"{'ISSUED' if commitment.approved else 'REFUSED'} - {commitment.reason}\n"
    )

    print("Audit log:")
    print(audit.render())
    print(
        "\nOutcome: the verified part moves, the unverified one never did, "
        "and every decision above can be shown to the customer."
    )


if __name__ == "__main__":
    main()
