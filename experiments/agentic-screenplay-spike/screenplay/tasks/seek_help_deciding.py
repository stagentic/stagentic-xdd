"""Task: run the decisions-demo workflow with a scripted list of options.

Builds a 'Scripted user responses' prefix from the options list and prepends
it to the generic run-decisions-demo task prompt."""
from screenplay_core import Actor
from stagentic_play import Agent


def seek_help_deciding(from_options: list[str]):
    def task(actor: Actor) -> None:
        prefix = "**Scripted user responses (in order):**\n"
        for i, option in enumerate(from_options, 1):
            prefix += f"{i}. `{option}`\n"
        prefix += "\n"
        actor.in_character(Agent).run_prompt("run-decisions-demo", prefix=prefix)
    return task
