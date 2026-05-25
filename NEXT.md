# NEXT

> Do not reference this file in commit messages. NEXT.md tracks the
> immediate next step and is rewritten as work lands; a commit that
> points at NEXT.md rots the moment the file changes.

## Introduce an agentic critic

Per ADR 0001, introduce a critic — a `claude -p` invocation that reads
the transcript and workspace and evaluates each scorecard characteristic
by LLM judgement — alongside the existing auditor, selectable by pytest
fixture.

The scorecard already holds the shape this needs: each entry has a
characteristic *description* (the natural-language target) and a
*failure* message. The auditor's `verify` lambda is its mechanism;
the critic uses the description as a prompt fragment instead.

Concrete shape to figure out:

- The fixture — pytest parametrisation over `auditor` and
  `critic`, so the same scenario runs under both.
- Critic correctness baseline — with the fake agent producing
  scene-exact output, the critic should agree with the auditor on
  every characteristic. Divergences are critic bugs until a real
  agent makes the question nontrivial.

## Starting point

The auditor lives in `play/src/auditor.py` as
`Auditor.evaluate(*, evidence, working_dir=None, scorecard)`, raising
`AssertionError(failures)` on any falsy `verify(transcript, working_dir)`.
The scenario in `spec/tests/test_red_green_commit.py` reaches it via
the `inspector` pytest fixture in `spec/conftest.py`. `_have` and
`_tree_diff` remain inline in the scenario file because the scorecard
rows close over them.

Develop the critic via ordinary TDD, not as a TDAB scenario (per
ADR 0001 point 4 — auditor and critic are harness code, their
behaviour driven by unit tests, not by scorecard rubrics).

The spike under `experiments/agentic-screenplay-spike/` prototypes
`claude -p` invocations from Python; treat as a source of ideas,
not a target shape (per ADR 0001).

The critic externally mimics the auditor: same
`evaluate(*, evidence, working_dir, scorecard)` signature, same
raise-on-failure / return-None behaviour. Internally, it prompts
`claude -p` with both paths and instructs the agent to use the
`Read` tool to inspect either. The response is parsed into
pass/fail verdicts per scorecard characteristic; failures go into
the AssertionError.

Suggested first move: TDD the critic in `play/` with the `claude -p`
call stubbed — get the skeleton green against the same unit-test
scenarios as the auditor, then swap the stub for a real invocation.

## Deferred

The "live constraint once the agent is real" — transient artefacts
(`.venv/`, `.pytest_cache/`, `__pycache__/`) polluting the
workspace; agent's cwd needing to be the workspace root — returns
when swapping `_fake_agent_performs` for `claude -p` becomes the
immediate next step.
