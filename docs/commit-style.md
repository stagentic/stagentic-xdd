# Commit message style

This commit style document supersedes any inferred style from past commit messages.

A commit message answers *why*, not *what* — the diff already records every edited line. The message earns its place by stating the motivating problem, constraint, or goal the change serves.

**State what is true after the commit, not how things were before.** *"commit guidance supersedes any inferred style from past commits"*, not *"past commits were being read as the style to follow"*.

**Subjects:** declarative, answering *why* the change is being made — the rationale, need, or constraint it serves. What has changed is in the change set, so doesn't need to be repeated; imperative voice (`add X`, `remove Y`) and bare mechanism narration (`X directive added`, `Y section removed`) do not belong in subjects — they describe what changed in place of why. Subjects from this repo that work:

- *"is_archivable must reject a run with no artefacts dir to write to"*
- *"a trailing comma keeps the transient-dir list vertical under ruff format"*
- *"commit messages should be clear and understandable with little context"*
- *"avoids permission denials by specifying the settings.json file to use"*

**A commit message must make sense to a reader who was not in the conversation.** Read the subject cold — no conversation, no diff — and say it out loud. If you would answer "what does that mean?", rewrite it. Name the things plainly, in the words the repo already uses, and leave the argument to the body.

Two ways this usually fails:

- **An epigram.** A turn of phrase instead of a statement. *"An honest red needs the gate in place, so the upgrade leads"* withholds which gate, which upgrade, and which part of the repo.
- **An abstraction.** The shape of a thing instead of the thing — "each move step", "the references", "the policy narrows". It only works for someone who was there. Write the concrete nouns.

Both of these answer *why* in the same number of words. Only the second says what is happening:

- cryptic: *"each move step lists the references it has to rewrite"*
- plain: *"an ADR moving to play must lose the links that point back here"*

**Planning sections are not a shared reference.** `§1` or `step 10` means nothing to a cold reader. A commit about `NEXT.md` itself may use them, but name the subject as well as the number.

**Bodies:** motivation first, framed around the current rationale. Don't enumerate the diff — listing every file modified or every item added repeats what the change set already shows. Brief supporting detail on mechanism is fine, but only after the why is clear.

**Bodies are held to the same plainness as subjects.** Short sentences. Name who does what. No compressed abstractions, and no reaching for a grander word than the plain one. A body that needs re-reading to parse has failed, however accurate it is.

**Format:** conventional commits — `<type>(<scope>): <subject>`.

**ADR commits:** layer the ADR status immediately after the type/scope prefix:
- `Status: Proposed` → `docs(adr): proposal: <subject>`
- `Status: Accepted` → `docs(adr): decision: <subject>`
- Other statuses (Rejected, Superseded, Deprecated) — use the status word by analogy.

**Commit proposals:** when proposing a commit for approval, always show the complete message verbatim — subject, blank line, body (if any), blank line, and trailer — exactly as it will be passed to `git commit -m`. After the message block, list the files to be staged.
