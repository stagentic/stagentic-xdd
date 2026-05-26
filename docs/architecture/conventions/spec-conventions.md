# Spec conventions

Naming and design-intent conventions for `spec/` that should persist across refactors. A fresh contributor might be tempted to "improve" these names; this document captures why each one is the way it is.

## The `transcript` variable

The local variable returned by `_fake_agent_performs(...)` is named `transcript`, even though today it is a `pathlib.Path` rather than a `Transcript` object. The same applies to the `evidence=` kwarg on `inspector.evaluate(...)`.

**Why:** the intent is to evolve `transcript` into a `Transcript` object that carries its own path (`.path`) and a method to read its contents (replacing the current `evidence.read_text()` inside `_then`). Naming declaratively today avoids a churning rename when the object lands. The kwarg name `evidence` follows the same principle — named for the contract (something that proves what the agent did), not the file shape.

**Not yet a thing:** do not pre-emptively introduce the `Transcript` object. Wait for a trigger — `_then` growing beyond `evidence.read_text()`, a second kind of evidence appearing, or the scorecard helpers being refactored.

## The `working_dir` parameter

The path bound to `working_dir` in `spec/tests/test_*.py` appears in three places: as a `copytree` destination during setup, as the `workspace=` kwarg to `_fake_agent_performs`, and as the second positional argument to `_have(...)` where the auditor reads it. All three keep the name `working_dir`, including the parameter inside `_have`.

**Why:** the auditor is not inspecting a separate "result" artefact. It is inspecting the working directory and asking "does this directory now reflect the expected end-state?" The working dir is the unified subject across all phases of the test; calling it `result` inside `_have` would imply a distinct produced artefact that does not exist. The lifecycle of one directory is what the test is about.

**Trigger to revisit:** if the auditor's contract genuinely changes — e.g. it begins evaluating something other than the working dir's state (a returned value, a side-channel) — that is the moment to revisit. Otherwise the name stays.
