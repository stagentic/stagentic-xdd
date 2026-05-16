from screenplay_core import Actor
from stagentic_play import Agent


def run_decisions_demo_with_one_option(actor: Actor) -> None:
    actor.in_character(Agent).run_prompt("run-decisions-demo-with-one-option")
