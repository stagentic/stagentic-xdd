# Spec conventions

Naming and design-intent conventions for `spec/` that should persist across refactors. A fresh contributor might be tempted to "improve" these names; this document captures why each one is the way it is.

## The `working_dir` parameter

The path bound to `working_dir` in `spec/tests/test_*.py` appears in four places: as a `copytree` destination during setup, as the `working_dir=` kwarg to `agent.perform`, as the `working_dir=` kwarg to `inspector.evaluate`, and as the second positional argument to `_have(...)` where the verify callables read it. All four keep the name `working_dir`, including the parameter inside `_have`.

**Why:** the auditor is not inspecting a separate "result" artefact. It is inspecting the working directory and asking "does this directory now reflect the expected end-state?" The working dir is the unified subject across all phases of the test; calling it `result` inside `_have` would imply a distinct produced artefact that does not exist. The lifecycle of one directory is what the test is about.

**Trigger to revisit:** if the auditor's contract genuinely changes — e.g. it begins evaluating something other than the working dir's state (a returned value, a side-channel) — that is the moment to revisit. Otherwise the name stays.
