# Commit message style

A commit message answers *why*, not *what* — the diff already records every edited line. The message earns its place by stating the motivating problem, constraint, or goal the change serves.

**Subjects:** declarative, answering *why* the change is being made — the rationale, need, or constraint it serves. e.g. *"A enables B"*, *"A will enable B"*, *"X reads cleaner when Y"*, *"X requires Y"*, *"A easier to B with C"*, *"X needs Y"*. Vary the framing — a log of repeated "X needs Y" subjects reads monotonously. What has changed is in the change set, so doesn't need to be repeated; imperative voice (`add X`, `remove Y`) and mechanism-narrating phrases (`X directive added`, `Y section removed`) do not belong in subjects — they describe what changed, not why.

**Bodies:** motivation first, framed around the current rationale. Don't enumerate the diff — listing every file modified or every item added repeats what the change set already shows. Brief supporting detail on mechanism is fine, but only after the why is clear.

**Format:** conventional commits — `<type>(<scope>): <subject>`.

**ADR commits:** layer the ADR status immediately after the type/scope prefix:
- `Status: Proposed` → `docs(adr): proposal: <subject>`
- `Status: Accepted` → `docs(adr): decision: <subject>`
- Other statuses (Rejected, Superseded, Deprecated) — use the status word by analogy.

**Commit proposals:** when proposing a commit for approval, always show the complete message verbatim — subject, blank line, body (if any), blank line, and trailer — exactly as it will be passed to `git commit -m`. After the message block, list the files to be staged.
