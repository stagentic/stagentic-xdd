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

## Deferred

The "live constraint once the agent is real" — transient artefacts
(`.venv/`, `.pytest_cache/`, `__pycache__/`) polluting the
workspace; agent's cwd needing to be the workspace root — returns
when swapping `_fake_agent_performs` for `claude -p` becomes the
immediate next step.
