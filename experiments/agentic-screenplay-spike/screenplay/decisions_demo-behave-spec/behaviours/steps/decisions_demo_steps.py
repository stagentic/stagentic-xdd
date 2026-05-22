"""Step defs for decisions-demo scenarios under behave.

Mirrors the pytest-bdd step defs but uses behave's `context` carrier and
`context.table` for datatables instead of pytest fixtures + a datatable
parameter."""
from behave import when, then

from screenplay_core import when as scr_when
from stagentic_play import then as scr_then
from tasks import seek_help_deciding
from expectations import complete_its_workflow


@when("the Decision Support Agent attempts to seek help deciding, with:")
def step_when_seek_help_deciding(context):
    assert context.table.headings == ["Options"], (
        f"expected Options column, got {context.table.headings}"
    )
    options = [row[0] for row in context.table]
    scr_when(context.decision_support_agent).attempts_to(seek_help_deciding(options))


@then("the Decision Support Agent should complete its workflow, as follows:")
def step_then_complete_its_workflow(context):
    assert context.table.headings == ["From", "Output"], (
        f"expected From|Output columns, got {context.table.headings}"
    )
    rows = [(row["From"], row["Output"]) for row in context.table]
    scr_then(context.decision_support_agent).should(
        complete_its_workflow(as_follows=rows, witnessed_by=context.inspector)
    )
