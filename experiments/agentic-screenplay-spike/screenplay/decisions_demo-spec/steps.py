"""Step definitions for decisions_demo-spec scenarios.

Imported from conftest.py for side-effect registration — pytest-bdd does
not auto-scan arbitrary modules for step defs, so this module must be
imported somewhere pytest already loads.

Two patterns per clause:
  - tabular variant (suffix `, with:` on When, `:` on Then) — extracts
    the first column from the datatable and passes it positionally to
    the resolved task/expectation factory.
  - bare variant — resolves the task/expectation and passes it through
    directly (the resolved object is already callable / decorated).

More-specific (tabular) patterns are registered first so they take
precedence over the bare ones when both could match a step line."""
import importlib

from pytest_bdd import parsers
from pytest_bdd import when as when_step, then as then_step

from screenplay_core import when
from stagentic_play import then


def _slug(phrase):
    return phrase.strip().lower().replace(" ", "_").replace("-", "_")


def _resolve(folder, phrase):
    name = _slug(phrase)
    module = importlib.import_module(f"{folder}.{name}")
    return getattr(module, name)


@when_step(parsers.parse("the {role} attempts to {task}, with:"))
def _when_attempt_with(
        request,
        role,
        task,
        datatable
):
    inputs = [row[0] for row in datatable[1:]]
    actor = request.getfixturevalue(_slug(role))
    when(actor).attempts_to(_resolve("tasks", task)(inputs))


@when_step(parsers.parse("the {role} attempts to {task}"))
def _when_attempt(
        request,
        role,
        task
):
    actor = request.getfixturevalue(_slug(role))
    when(actor).attempts_to(_resolve("tasks", task))


@then_step(parsers.parse("the {role} should {expectation}, as follows:"))
def _then_should_with(
        request,
        inspector,
        role,
        expectation,
        datatable
):
    rows = [tuple(row) for row in datatable[1:]]
    actor = request.getfixturevalue(_slug(role))
    expectation = _resolve("expectations", expectation)

    then(actor).should(expectation(
        as_follows=rows,
        witnessed_by=inspector)
    )


@then_step(parsers.parse("the {role} should {expectation}"))
def _then_should(
        request,
        inspector,
        role,
        expectation
):
    actor = request.getfixturevalue(_slug(role))
    expectation = _resolve("expectations", expectation)

    then(actor).should(
        expectation(
            witnessed_by=inspector
        )
    )
