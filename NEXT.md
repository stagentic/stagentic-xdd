# NEXT

## Make the critic swappable; introduce an agentic critic

Per ADR 0001, the then-step is to evolve the in-process auditor
(regex / file-existence / tree-diff predicates) into a critic — a
`claude -p` invocation that reads the transcript and workspace and
evaluates each scorecard characteristic by LLM judgement —
selectable by pytest fixture.

The scorecard already holds the shape this needs: each entry has a
characteristic *description* (the natural-language target) and a
*failure* message. The auditor's `verify` lambda is its mechanism;
the critic would use the description as a prompt fragment instead.

Concrete shape to figure out:

- The eval interface — what does a critic/auditor receive
  (transcript text, `working_dir` path, scorecard entries) and
  return (per-characteristic verdict + reasoning)?
- The fixture — pytest parametrisation over `auditor` and
  `critic`, so the same scenario runs under both.
- Critic correctness baseline — with the fake agent producing
  scene-exact output, the critic should agree with the auditor on
  every characteristic. Divergences are critic bugs until a real
  agent makes the question nontrivial.
- Evidence the critic sees — the transcript via `.read_text()` is
  obvious; what about workspace state? Either give the critic a
  tree listing + selected file contents, or let it use a `Read`
  tool against the workspace path.

## Starting point

Nothing critic-related exists yet. The auditor lives inline in
`spec/tests/test_red_green_commit.py` as `_have`, `_then`,
and `_tree_diff` helpers; there is no separate evaluator module
and no critic of any kind.

Develop the critic via ordinary TDD, not as a TDAB scenario (per
ADR 0001 point 4 — auditor and critic are harness code, their
behaviour driven by unit tests, not by scorecard rubrics).

The spike under `experiments/agentic-screenplay-spike/` prototypes
`claude -p` invocations from Python; treat as a source of ideas,
not a target shape (per ADR 0001).

Suggested first move: extract the eval interface from the inline
helpers in `test_red_green_commit.py` — something that
takes a scorecard (list of rows) plus evidence (transcript text,
`working_dir` path) and returns per-characteristic verdicts. With
that shape in place, the auditor becomes one implementation and
the critic can land as another, swapped via fixture.

## Deferred

The "live constraint once the agent is real" — transient artefacts
(`.venv/`, `.pytest_cache/`, `__pycache__/`) polluting the
workspace; agent's cwd needing to be the workspace root — returns
when swapping `_fake_agent_performs` for `claude -p` becomes the
immediate next step.
