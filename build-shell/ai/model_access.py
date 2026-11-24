"""Boreal Field Services - model access (AI Core / GenAI Hub side).

This is where Python lives in the architecture: managed AI runtime and
model access for the agents. The CAP application layer is Java or
Node.js, there is no Python CAP, and the Joule Studio agents themselves
are configured, not coded.

The agents' decision logic does not wait on a model connection. It is
implemented and tested in this layer, in stock_picture.py (what counts
as confirmed stock) and gates.py (what may proceed, and who approves),
and run end to end by run_morning.py. Those modules are deterministic
on purpose: a gate that guards a medevac deadline must give the same
answer every time.

This module is the one deliberate placeholder: the live model calls.
No endpoints, no credentials, no calls are made from here.
"""


def get_model_response(prompt: str) -> str:
    """Placeholder for a GenAI Hub model call.

    Real build: route through AI Core / GenAI Hub with Responsible AI
    controls (content checks, audit logging via governance/).
    """
    raise NotImplementedError("No model is connected in the simulation.")


def summarise_failure_history(equipment_id: str) -> str:
    """Placeholder: support Scout's triage with a history summary."""
    raise NotImplementedError("No data source is connected in the simulation.")
