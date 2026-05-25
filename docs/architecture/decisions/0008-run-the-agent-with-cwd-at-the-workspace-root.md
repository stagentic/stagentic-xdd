---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0008 — Run the agent with cwd at the workspace root

**Status:** Proposed

## Context

ADR 0001 sets the strategy of swapping `_fake_agent_performs` for a `claude -p` invocation once the harness is green. ADR 0007 establishes the task chain: each task has a `scene/` directory, copied into a tmp workspace as the agent's starting state. Neither ADR specifies *where the agent is invoked from* — its current working directory at the moment `claude -p` runs.

The cwd is not incidental. Claude Code discovers `CLAUDE.md` files (and `.claude/` plugins) by walking up from cwd to the filesystem root, plus loading the user-level `~/.claude/CLAUDE.md`. Verified empirically: from `/tmp/`, `claude -p` does not load this repository's root `CLAUDE.md`. Discovery is cwd-relative, not parent-process-relative.

This makes the choice of cwd architecturally significant:

- If cwd is inside the repo (repo root, `spec/`, etc.), the agent inherits the harness's own `CLAUDE.md` — including any spec internals, scorecard descriptions, or development meta-context. Test and System Under Test are no longer separated.
- If cwd is the tmp workspace (outside the repo), the agent sees only `~/.claude/CLAUDE.md` plus whatever the scene placed into the workspace itself.

The second case yields two distinct architectural properties:

1. **Isolation by construction.** No repo-level documentation reaches the agent. Spec internals can stay in this repository's `CLAUDE.md` without leaking to the System Under Test.
2. **Per-scene seeding capability.** A `CLAUDE.md` (or `.claude/CLAUDE.md`) placed under a `scene/` directory will be auto-loaded by the agent at task time, because `copytree` puts it into the workspace and Claude Code discovers it from cwd.

## Decision

1. **The agent's cwd is the workspace tmp directory** — the same directory the scene was copied into. The harness sets cwd explicitly when invoking `claude -p`; it does not inherit the test runner's cwd or default to the repo root.

2. **No mechanism is introduced that re-attaches the agent to the repo.** No `--add-dir` pointing at the repository, no env var that resolves back into it, no symlinks into repo paths from the workspace.

3. **Per-scene `CLAUDE.md` is the supported way to seed agent-facing context.** A scene MAY include `CLAUDE.md` (or `.claude/CLAUDE.md`). The agent will discover it when its cwd is the workspace. No scene is required to include one.

4. **Repo-level `CLAUDE.md` is for harness contributors only.** Its contents are not part of the agent's context boundary.

## Consequences

- The harness/SUT boundary is enforced by cwd choice, not by where information happens to be filed. Spec details can live in this repository's `CLAUDE.md` without leaking to the agent.
- Per-task agent conventions become a scene authoring concern: dropping a `CLAUDE.md` into a scene flows it to the agent for that task and every subsequent task that inherits it through the chain.
- The agent inherits user-level Claude Code config from `~/.claude/CLAUDE.md` — same as any other Claude Code invocation on the same machine. This is desirable: user-side guardrails apply uniformly.
- A future harness change that moves the agent's cwd into the repo (for any reason — debugging, alternative harness shape, accidental refactor) breaks the isolation invariant. Such a change must either preserve isolation deliberately (e.g. `claude -p --bare`) or document that it accepts the leak.
- The xdd skill — the System Under Test — does not yet exist in this repository. When it does, it will be staged into the workspace by the harness (a one-way copy into the workspace's `.claude/skills/` directory) so the agent discovers it via cwd-relative lookup. The mechanism is deferred to a follow-up ADR; this ADR records only that skill provisioning happens *through* the workspace, never by attaching the agent to repo paths.
- The `prompt.md` mechanism in ADR 0007 (task description, ignored by the fake agent, read by the real agent) is the primary channel for telling the agent what to *do*. A per-scene `CLAUDE.md` is the complementary channel for ambient conventions about the workspace — not a replacement.

## Alternatives considered

- **Invoke the agent with cwd at the repo root.** Simplest to wire up; allows the agent to read repo-level `CLAUDE.md` and `.claude/` plugins. Rejected: risks polluting the agent's context with information that makes it aware it is being tested — including the scorecard characteristics the auditor checks for and the TDAB framing of the harness — which would compromise the integrity of the results.
- **Use `--bare` for full isolation.** Strips all auto-discovery — including legitimate user-level `~/.claude/CLAUDE.md`, hooks, MCP, plugins. Useful as an override for cases that need absolute isolation, but too aggressive as the default.
- **Pass task and convention context to the agent via a CLI arg or prompt parameter rather than CLAUDE.md.** Workable, but ignores Claude Code's idiomatic context mechanism. The `prompt.md` + scene `CLAUDE.md` split keeps "what to do" separate from "how this workspace works" using native primitives.
- **Place ambient agent context at the user level (`~/.claude/CLAUDE.md`).** Bleeds into every Claude Code invocation on the same machine, not just the harness. Rejected.
