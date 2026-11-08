# NEXT

> Do not reference this file in commit messages except those about this file itself.
> NEXT.md tracks the immediate next step and is rewritten as work lands (without 
> any mention of what was just completed.

## 0. Open decisions blocking §1

An audit of §1's plan against the ADRs as they stand turned up twelve items, in three
groups. The first is settled. The second needs a decision before the plan can be
followed. The third is correction work on §1 that is understood but not yet applied.

### 0.1 How the critic is tested — settled enough for §1 to proceed

**Decided: play owns critic validation, and 0024's critic check moves into a proposed
play record for it.** Step 10 needs that ownership and nothing more, so the method
stays open and is decided on its own.

The rest of this section argues for replacing that method. It is kept here for when we
take that decision up.

What started it:

> §1 says it two ways — the inverted skill "leaves 0024", and play gets "the critic
> check, which is where the inverted skill ends up". But as 0024 is written, that check
> runs the **spec suite** against an inverted **`SKILL.md`** and grades **spec's
> scorecard rows**. An extracted play has none of those. So either play's critic
> validation is the canned-transcript contract test *only*, and the inverted skill
> stays an xdd concern, or 0024's check doesn't move.

Inverting the scorecards is probably the wrong choice anyway: spec's scorecards will
change over time and there will be more of them, so anything keyed to inverting all of
them drifts by construction.

**What the critic actually is.** A `claude -p` call taking a transcript plus prose
characteristics, returning per-row PASS/FAIL. Critic rows carry only
`{characteristic, failure}` — no `verify` lambda, that is the Auditor's. So the critic
is **domain-agnostic**: xdd's scorecard is one input, not part of its definition.

**play's test: invented characteristics, graded by difficulty, both directions.** play
needs no xdd vocabulary — only `(characteristic, transcript, expected verdict)` triples
of its own making. *"The transcript contains a greeting"* against a transcript with
"hello" expects PASS; against one with none, expects FAIL. Two things that buys which
the inverted skill never did:

- **Both directions.** A critic that fails everything is as broken as one that passes
  everything. The inverted skill only tested the FAIL direction.
- **Graded difficulty.** A trivial characteristic can pass while judgement on subtle
  ones has degraded. A set ordered from unambiguous to subtle says *where*
  discrimination broke on a new version, not just whether it is gone.

**spec's question is different, and probably real.** A critic handling "contains a
greeting" may still misread *"failing for the right reason"*. Those are domain
judgements play cannot cover without importing its client's vocabulary. So spec's shape
is the same mechanism at its own level: **per characteristic, one transcript that should
fail it and one that should pass**, with the fixtures beside the scorecard row they
test.

**That solves the drift that sank the inverted skill.** A whole-file inverted copy
drifts silently against a scorecard that gains rows. A fixture pair attached to a row
drifts visibly — a row with no fixtures is obvious, and adding a row means adding its
pair.

**And it dissolves the diagnosis.** 0024's three-way branch — stale copy, agent didn't
comply, critic blind — exists only because the inverted skill routes through a live
agent. With known transcripts there is no agent to blame and no copy to drift. A
failing fixture means the critic.

**One objection answered.** These are canned transcripts, which 0024 currently rejects:
*"a fixed transcript doesn't change with the version under test."* That conflated two
questions. *Does the agent behave?* needs real runs — the scenarios. *Does the critic
discriminate?* needs known inputs. The rejection was right for the first and wrong for
the second.

**Counted: ten critic characteristics** — nine in `test_write_a_failing_test`, six in
`test_make_the_failing_test_pass`, five shared. Every one also carries a `verify`
lambda, so no row is critic-only today.

That changes the cost twice over. The critic is handed a transcript *and* a workspace,
and four of the ten rows are judged on the workspace, so a fixture is a pair of
directories rather than a file. But one passing fixture satisfies every row in its
scenario at once, so only the failing direction needs one per row — roughly twelve
fixtures, not twenty, and
`tasks/1-first-test-for-miles-to-km-converter/scene` plus its `transcript.md` is
already one of the passing pair.

Nothing is sunk in the method this would replace: no `SKILL-inverted.md` exists
anywhere in the repo.

### 0.2 What status marks a relocated ADR

0013, 0016 and 0017 are **Accepted** and still in force in `play/src`. ADR 0000 defines
`Deprecated` as a reasoning-trail status, so marking them that way tells a reader the
decision was withdrawn. Needs a different status, or wording that names the relocation.

### 0.3 Whether forking 0011 for play makes sense

0011's decision names `stagentic-test` (`src/stagentic/test/matchers.py`) as the home of
the `matching` alias — a project that does not travel with play. The same problem §1
dismisses for 0012.

### 0.4 Which numbers the new xdd records take

§1 steps 9 and 10 mint new xdd records at repo level. §2 already reserves 0026 (the
sessions-model pin), 0027 (split testing) and 0028 (a second vendor). Nothing says which
numbers the split halves get.

### 0.5 Whether 0019 is revised before it moves

§9 records that 0019's factual premise is stale — effort and the context window are both
readable back on 2.1.220. Moving it as written carries the staleness into play.

### 0.6 Corrections to §1, understood but not yet applied

- **The inlining claim is wrong by about six times.** §1 says two citations need
  inlining. Verified across the five movers: **thirteen sites touching eight repo-level
  records**. 0013 cites 0001, 0007, 0009, 0010, 0011. 0008 cites 0001, 0007. 0016 cites
  0002, 0008, 0009. 0014 cites 0010 plus `../../working-practices.md` — itself a `../`
  escaping `play/`. 0017 cites 0002, 0003, 0014, 0015, 0016. Steps 5, 7 and 8 carry no
  inlining instruction at all.
- **`play/` already points outside itself and no step touches it.**
  `play/README.md:131,149` and `play/HOW_IT_WORKS.md:42,103` link
  `../docs/architecture/decisions/…` and `../COMMANDS.md`. Step 6 moves 0016, so two
  become links into a repo tombstone. `play/pyproject.toml:22` has
  `path = "../stagentic-test"`.
- **Four more files belong in "Beyond the ADRs":** `docs/working-practices.md`
  (play-bearing, and linked from 0014 which moves), `docs/architecture/improvements/`
  (both files are about `play/src`), `.claude/hooks/` (one encodes play's mutation loop,
  one injects working-practices), and `test-conventions.md:148`'s bare "ADR 0011" — step
  3 moves that file and would create the violation step 12 exists to catch.
- **Step 11 depends on work no step performs.** It needs play's model declaration from
  step 10, but step 10 only writes ADRs. Building it — `tomllib` read, `ClaudeCli`
  taking a model parameter — is §2's "Building what 0023 decides", not one of the twelve
  steps.
- **"The commands split with them" is wrong for `scripts/`.** All five drive
  `uv run --directory spec`, and 0024/0025 link five COMMANDS.md anchors for them. Those
  stay at repo level; only §6's underlying N× mechanism is play's.
- **Repo→moved-record citations are never budgeted for.** The rule is symmetric, the
  work list is not: 0022:17,38 cite 0008 and 0016; 0023:59,70 cite 0017 and 0016;
  0019:15 cites 0017.
- **0008's xdd residue is more than §3's scene concession.** Also xdd-side: the
  Consequences bullet on staging the xdd skill into the workspace, the "per-task agent
  conventions become a scene authoring concern" bullet, and the first Alternative naming
  the scorecard characteristics and the TDAB framing. §4 (repo-level `CLAUDE.md`) is
  about this repo too, not an extracted play.

## 1. Restructure the ADRs by project

`play` is destined to become `stagentic-play`, a separate library, so its decisions
should travel with it. Today they sit in one sequence alongside the xdd skill's and
the repo's, and six of twenty-six records decide something for both.

### What made this urgent

`play` ships prompts of its own — the critic's, and the transcriber's. Those are as
version-sensitive as `SKILL.md`, so a consumer pointing `stagentic-play` at a newer
model cannot assume the critic still reports faults. That gives `play` its own
version-validation story, and the ordering falls out of the dependency chain
`stagentic-test` → `play` → `spec`/xdd: a `play` validated on the new version has to
come first, because xdd's scenarios are graded by play's critic.

Three things follow, none started:

- **A critic contract test.** `FakeAgent` with a canned failing transcript and the
  real critic, marked `contract`, in `play/tests/contract/`. It answers "can this
  critic report a fault at all" — cheaply, deterministically, on every full baseline
  rather than only when someone remembers a migration step. Total blindness is the
  failure that makes a whole confirmation meaningless.
- **Versioning play's real-claude tests.** A contract test asserting the critic
  reports a fault is asserting that about one model version, so a green means nothing
  without knowing which. **Decided: `play` declares its own versions for its own
  tests**, rather than reading `spec/models.toml` — that would invert the dependency
  and break the moment `play` is installed standalone. Cost accepted: nothing reports
  when play's declaration and spec's drift apart.
- **0024 shrinks.** Once play owns "does the critic still report faults", the inverted
  skill leaves 0024 entirely — the term, `### The Critic Check`, the
  `SKILL-inverted.md` artefact, the drift-against-the-scorecard problem, and the
  three-way diagnosis. 0024 becomes: validate the xdd skill on a new version, against
  a critic play has already validated.

### The classification

"Conflated" means the record decides something for both, not merely that it mentions
the other.

| # | Title | Category | Note |
|---|---|---|---|
| 0000 | Use ADRs to record decisions | repo-wide | play's repo needs its own copy of the convention |
| 0001 | TDAB with vanilla pytest | conflated → xdd | §1–2 are the scenario method; §3 decides play's auditor→critic fixture swap |
| 0002 | Pin CLI version | superseded | by 0022 + 0024 |
| 0003 | Pin model versions | superseded | by 0023 + 0024 |
| 0004 | Guidance, guardrails, gateways | conflated → xdd | guidance is the skill (0018 is "the guidance leg"); guardrails and gateways are enforcement play owns |
| 0005 | Periodic CLI update checking | repo-wide | still "To be determined"; both layers need it |
| 0006 | Native installer for the pinned CLI | repo-wide | |
| 0007 | Task chain audited by a scorecard | conflated → xdd | `spec/tasks/` and scenes are xdd; §4 fixes play's `Agent` contract — `task, in_workspace → transcript_path` |
| 0008 | cwd at the workspace root | conflated → play | §1–2 and §4 are the harness's; §3's per-scene `CLAUDE.md` concession is xdd's |
| 0009 | Select inspector and agent via pytest options | xdd | re-read: the decision is entirely `spec/conftest.py`'s options and defaults. That the implementations are interchangeable is 0013's, not this record's |
| 0010 | Mutation testing | repo-wide | |
| 0011 | PyHamcrest | repo-wide | "starting with `play`" |
| 0012 | Path-source packages | repo-wide | created what is now `stagentic-test` |
| 0013 | Agents and inspectors return a Result | play | clean |
| 0014 | Separate jsonl translation from the transcriber | play | clean |
| 0015 | Capture xdd-skill missteps as lessons | xdd | clean — "scope is the xdd skill only" |
| 0016 | Permissions as a launch argument | play | reads a scene's file, but the decision is `ClaudeCli`'s |
| 0017 | Record CLI version and model in the transcript | play | clean |
| 0018 | Build the xdd skill as a corrective skill | xdd | clean |
| 0019 | Pin and record reasoning effort and context window | play | re-read: it decides `--effort high` as a harness constant in `play/src/claude_cli.py`, and the header is `ClaudeTranscriber`'s. No spec declaration in it; the only xdd tie is the 0015 provenance motive. §9 also records its premise as stale on 2.1.220 |
| 0020 | Frontmatter description drives invocation | xdd | clean |
| 0021 | `stagentic` namespace | repo-wide | |
| 0022 | Pin the Claude Code CLI version | repo-wide | re-read: it decides `DISABLE_AUTOUPDATER=1` and a version in `README.md`. Neither touches play code, so play needs a *counterpart*, not a split |
| 0023 | Pin the model version used by spec runs | conflated | `--model` is passed by play's `ClaudeCli`; the declaration is spec's — and play now needs its own |
| 0024 | Validate a version change | conflated | the critic check belongs to play; the skill validation is xdd |
| 0025 | Distil the skill to its minimum | xdd | clean |

5 clean play, 5 clean xdd, 8 repo-wide, 6 conflated, 2 superseded.

Two split evenly: 0023 and 0024 — plus 0004, which probably comes off the list (see
below). Three are lopsided: 0007's play content is one clause, 0008's xdd content is
§3's scene concession and some of its Consequences and Alternatives, and 0001's play
content was superseded in practice by 0009 and 0013. Move those whole to their owner
and relocate the stray material, rather than minting a one-clause record.

### The layout

This repo is the xdd plugin's. So anything xdd — `spec/` included — and anything
repo-wide stays at the repo level in `docs/`. `play/` gets its own `docs/`, because it
will be extracted. `stagentic-test/` will likely be extracted too, but has no
decisions of its own today, so it gets nothing yet — and whoever extracts it inherits
this same exercise.

That collapses the classification: **only play's records move**. Two sequences, not
three, so repo-level references stay bare ("ADR 0018") and play's need qualifying
("play ADR 0003"). Ten records are affected, not twenty-six:

- **Move whole**, leaving a Deprecated tombstone in place so the sequence has no gaps:
  0013, 0014, 0016, 0017. And 0008, once §3's scene concession is relocated into 0007.
- **Split**, superseded by an xdd record here and a new record in play: 0019, 0022,
  0023, 0024.
- **Need a play counterpart**, so play can stand alone: 0000 (its own ADR convention),
  0005 and 0006 (installing and tracking a CLI), 0010, 0011 (practices play follows),
  0021 (the namespace). 0012 does not — path-source packages describe this monorepo
  and mean nothing to an extracted play.
- **0004 probably comes off the list.** Its taxonomy is how *xdd* controls an agent;
  play merely supplies mechanisms. Re-examine rather than split.
- **Superseded records stay put.** 0002 and 0003 are history and do not move.

Document the layout in a contributors doc at the repo root, referenced from
`README.md` and `CLAUDE.md`.

### play's own sequence

play renumbers from 0000 — the moved records take play's next numbers, not their repo
numbers. So the move order is play's permanent sequence, and it is ordered to read as
an introduction to the framework rather than to preserve this repo's chronology.

The one hard constraint: a play record must not cite one that has not landed yet, or
it points out of `play/` — the direction that breaks on extraction.

| play | from | reads as |
|---|---|---|
| 0000 | — | new — play's own ADR-about-ADRs |
| 0001 | 0013 | **the contract** — agents and inspectors return a Result |
| 0002 | 0008 | **the agent's boundary** — cwd at the workspace root |
| 0003 | 0016 | **completing that boundary** — permissions as a launch argument |
| 0004 | 0014 | **reading a run back** — separate jsonl translation from the transcriber |
| 0005 | 0017 | **what the transcript carries** — the resolved CLI version and model |

Citations point backwards: 0003 cites 0002 ✓, 0005 cites 0004 and 0003 ✓. Two point at
records staying at repo level and must be inlined as prose when they move — 0013's
mention of 0009, and 0016's mention of 0009.

New and forked records land after these, numbered as they are decided: play's CLI pin,
its own model-version declaration, its critic validation, the play half of 0019, and
the forks of 0005, 0006, 0010, 0011 and 0021.

### The plan

Each row is one commit, and ends by ticking its box here — this checklist is all a
fresh session has after `/clear`.

**The invariant that keeps each step safe:** every commit leaves all links resolving.
During the migration a repo-level record may point into `play/docs/` — legal, because
`play/` is still in this repo. Step 12 severs what remains, and the grep test below is
the definition of done. Without that allowance the mutually-citing cluster could only
move in one large commit.

- [ ] **1.** Contributors doc at the repo root: the layout, the two sequences, the
  no-cross-reference rule, fork-not-sync, how to cite a play record in prose.
  Referenced from `README.md` and `CLAUDE.md`.
- [ ] **2.** `play/docs/architecture/decisions/` scaffolding — play's `0000`,
  `README.md` index, `TEMPLATE.md`.
- [ ] **3.** Move `src-conventions.md` and `test-conventions.md` to `play/docs/`;
  create `play/CLAUDE.md` pointing at them; prune the root `CLAUDE.md`'s play triggers.
- [ ] **4.** play 0001 ← 0013. Inline its mention of 0009.
- [ ] **5.** play 0002 ← 0008. Relocate §3's scene concession into 0007.
- [ ] **6.** play 0003 ← 0016. Inline its mention of 0009.
- [ ] **7.** play 0004 ← 0014.
- [ ] **8.** play 0005 ← 0017.
- [ ] **9.** Split 0019 — supersede it with an xdd record and a play record.
- [ ] **10.** Rewrite 0022, 0023, 0024 in split form. Each produces an xdd record here
  and a play record — these are where play gets its version story, not separate new
  decisions:
  - 0022 → **xdd:** hold the CLI version scenario runs are validated against.
    **play:** hold play's own CLI version for its real-claude tests.
  - 0023 → **xdd:** the model version spec runs name on every call.
    **play:** play declares its own model versions for its own tests.
  - 0024 → **xdd:** validate the skill on a new version.
    **play:** validate play's prompts on a new version. The critic check moves here
    whole — the inverted skill, its artefact and its three-way diagnosis — as the
    method the record inherits. Whether that method survives is §0.1's question, and
    it does not hold this step up.

  Commits as one step: the three cite each other, 0025 cites all three, and 0002/0003
  point forward to them. That is why this one cannot subdivide.
- [ ] **11.** The critic contract test — `FakeAgent` + a canned failing transcript +
  the real critic, TDD, marked `contract`. Needs play's model declaration from step 10,
  so it knows which version it is asserting about.
- [ ] **12.** `COMMANDS.md` play counterpart; sever the remaining repo↔play links; run
  the grep test; tidy both indexes.

Each move is the same three edits: write play's version, deprecate the original in
place with a prose note naming the *title* rather than a play number — a number cited
across the boundary goes stale and cannot be link-checked — and update both indexes.

**A concrete test for "done":** copy `play/` out on its own and nothing in it points
outside itself. Greppable — no `../` escaping `play/`, and no bare ADR numbers that
mean repo-level records.

### Rules agreed

- **No cross-project ADR references.** An xdd record does not link a play record, or
  the reverse. Once play is extracted those become links out of the repository, which
  the portability rule forbids.
- **A record that moves is deprecated with a note** saying it has moved to play — in
  prose, without a link. See ADR 0000 for the statuses.
- **A play counterpart is a fork, not a sync.** At the split the copies diverge and
  neither is authoritative for the other.

### Beyond the ADRs

- **Conventions.** `src-conventions.md` and `test-conventions.md` describe `play/src`
  and `play/tests`, so they move to `play/docs/`. `spec-conventions.md` stays. Both are
  cited from `CLAUDE.md` and from §11's lens lists.
- **`play/CLAUDE.md` does not exist.** Play's working instructions live inside the root
  `CLAUDE.md` today, so an extracted play arrives with none. Create it so it travels.
- **`COMMANDS.md` is repo-level and holds play's commands.** Needs a play counterpart,
  on the same fork-not-sync basis.
- **`scripts/`** — `verify-runs.sh`, `compare-wordings.sh`, `tally.sh`, `fisher.sh` —
  are interim, and §6 puts their successor in play. The commands split with them.
- **`docs/migrations/`** stays xdd, but play needs its own once it validates the critic
  prompt.
- **`decisions/README.md`** needs Deprecated rows and a prose pointer to where play's
  records live. Prose, not a link — that link breaks the day play leaves.

### How `play/CLAUDE.md` will load

Checked against the Claude Code docs: CLAUDE.md files in the hierarchy *above* the
working directory load at launch, and files in **subdirectories load on demand, when
Claude reads a file in that directory**. So `play/CLAUDE.md` is picked up
automatically, but lazily — not at session start.

That is the behaviour wanted: scoped to play, and it travels with play. Three
consequences.

- **Anything needed before touching play stays in the root `CLAUDE.md`.** The
  full-baseline-at-session-start rule is the example — it runs play's suites, so it has
  to be in context at launch.
- **Move, don't duplicate.** The docs warn that contradictory rules across nested
  CLAUDE.md files are resolved arbitrarily, so the root file's play sections get
  deleted as they move rather than left behind as a summary.
- **Two tempting shortcuts to avoid.** `@play/CLAUDE.md` from the root file expands at
  launch, which defeats the laziness, and its path breaks when play leaves.
  `.claude/rules/` with `paths:` frontmatter gives the same scoping, but rules live in
  the project's `.claude/`, so they would not travel either.


## 2. Finish the version-pinning ADRs

**Held pending §1.** 0022 to 0025 are written and reviewed but stay uncommitted:
two of the six conflated records are in that set, so committing them now would mean
superseding them immediately.

Eight records cover pinning a version, changing it, reducing the skill afterwards,
and where this is heading. Nothing above 0021 is committed, so numbering and
titles are still free to change.

They are numbered as they were decided, not grouped by subject, and listed below
in the order we expect to write them. 0022 to 0025 are the set under review; 0019
exists and is blocked; the rest are unwritten.

| ADR | Covers | State |
|---|---|---|
| 0022 | Pin the Claude Code CLI version | Reviewed section by section. |
| 0023 | Pin the model version used by spec runs | Reviewed section by section. |
| 0024 | Validate a version change with repeated suite runs; migrate one version at a time | Reviewed whole-document. Shrinks under §1. |
| 0025 | Distil the skill to its minimum on a model change | Drafted, reviewed in a loop. Holds the measure-then-reduce method. |
| 0026 | Pin the model version for Claude Code sessions in this repository | Not written. A fresh decision, not a supersession. See below. |
| 0019 | Pin and record reasoning effort and the context window | Proposed. Needs the per-call seam 0023 introduces, so it cannot be acted on until 0023 is built. |
| 0027 | Split testing across models and versions | Not written. See below. |
| 0028 | Run the scenarios against a second vendor | Not written. See below. |

0022 to 0025 commit together: each links to the others, and 0002 and 0003 point
forward to them. 0026 can follow separately, since nothing existing links to it.

### 0026 — the model version for sessions in this repository

`.claude/settings.json` sets `ANTHROPIC_DEFAULT_OPUS_MODEL` and its siblings for
every Claude Code session started here. ADR 0003 set them intending to control
spec runs, which they do not. What they do control is the model a contributor or
agent works on inside this repository, and that effect has no record behind it
once 0003 is superseded.

The rationale is provenance. The observations that drive this project come out of
those sessions — the missteps captured as lessons under ADR 0015 especially. A
lesson says the agent got something wrong, and that claim is only attributable if
the model that got it wrong is known. Item 8 below treats reasoning effort as
bearing on the same provenance.

A second, softer reason: contributors get the same agent behaviour as each other,
so shared working practices behave consistently rather than per-person.

It has the limitation ADR 0022 records for the CLI version — the entries only
apply to sessions started in this repository.

### Building what 0023 decides

0023 records the measurements showing why each `claude -p` call has to be given
the model version as an argument, rather than inheriting it from the environment
a spec run starts in. It decides `--model <version>`, that the agent and the
critic are pinned separately, and that the versions are declared in
`spec/models.toml` under `[agent] model` and `[critic] model`, and that no
environment variable overrides them. What is left is building it:

- `conftest.py` reads `spec/models.toml` with `tomllib` and passes each role's
  version into its `ClaudeSession`.
- `ClaudeCli` takes a model parameter and puts `--model <version>` on the command.
  It does not read the configuration file, so `play` stays extractable.

The model entries in `.claude/settings.json` stay as configuration with no record
behind them until 0026 is written.

### 0027 — split testing, later

Lists of versions rather than one, the agent and the critic configured separately,
and comparative runs driven by a fixture. Adding a version to the agent, running
the spec, then bumping the critic separately.

The ordering point that used to sit here — bump the critic first and confirm it
still catches a seeded fault — is now 0024's, and moves to play under §1.

Trying a candidate version belongs there too, and the preferred way is a pytest
option — `--agent-model` and `--critic-model`, defaulting to `spec/models.toml`.
Two arms can then run at the same time on different versions, which
swapping a file cannot do; that is why `compare-wordings.sh` alternates arms
sequentially. It also leaves the version in the command that produced a batch of
artefacts, and mutates nothing in the working tree.

### 0028 — a second vendor, later still

Running the same scenarios against another service — Codex alongside Claude. The
seam already exists: `Agent` and `FakeAgent` share
`perform(task=, working_dir=) -> Success`, and ADR 0009's `--agent` option selects
between them, so a vendor implementation is a third one. `ClaudeSession`,
`ClaudeCli` and `ClaudeTranscriber` sit below that as injected collaborators, and
each would need a counterpart — the transcriber most of all, since it parses
Claude's session JSONL.

`spec/models.toml` keys on role rather than vendor, so a vendor entry slots in
beside `model` when there is a second implementation to name. Adding one before
then would be wiring with nothing behind it.

Item 6 below is the `play` implementation of the repeated-run mechanism these
records rely on; this item is about recording the decisions.

When these land, add a trigger to the *What to read when* list in `CLAUDE.md`
covering both a wording change and a version change, pointing at 0024 and 0025.

## 3. Capture code-change diffs in the run transcript — Edit still to do

The captured `transcript.md` (produced by `ClaudeTranscriber`) renders a tool use
as only its `file_path`, so what the agent changed can be invisible to a reviewer
or critic reading the transcript.

**Write — done.** A Write now renders the content it wrote as a fenced block, by
default (the branch-by-abstraction seam is collapsed and the approval masters
migrated).

**Edit — still to do.** Render the before/after (`old_string` → `new_string`) as a
diff. The JSONL already carries the full tool input. TDD in `play`
(`claude_transcriber.py`) — extend the current transcriber, rather than waiting on
the ground-up rewrite in ADR 0014.

## 4. Observed Misstep: Added multiple cases to a test all at once

Introducing a parametrised `case` is introducing a test, so adding more than one
case at once writes several failing tests before any production change — the same
smallest-step break as composing several plain test methods up front. A `case`
earns its place only to remove or avoid duplication, and lands across two commits:

1. **Refactor** the existing single test into the parametrised shape over its one
   present case — behaviour-preserving, no new assertion (structural).
2. **Add** the next case as its own behavioural commit; one case per commit
   thereafter.

**Still to do:**
- Add a scenario to `spec/tests/test_red_green_commit.py` that judges an agent
  introducing cases this way — one at a time, refactor-first — rather than
  landing a multi-case parametrised block in a single step.
- Work out how to build the scene that recreates the misstep: the opening
  workspace state that tempts an agent into adding several cases at once.

## 5. Observed Misstep: Started TDD at the innermost unit

The change was driven from `ClaudeCli` — the deepest collaborator — rather than
from the failing scenario. Adding its new required parameter meant threading the
argument up through every caller before anything could go green: eight call sites
in its own test file, the contract test, a test double's signature, and
`ClaudeSession`. None of that work was the change; it was the cost of having
started underneath it.

Worse, the question the change actually turned on — who owns the knowledge that a
scene keeps its permissions at `.claude/settings.json` — surfaced mid-cascade,
with the code already half-changed. Working outside-in asks it first: start at the
scenario that fails, descend one collaborator at a time, and each red is about the
seam being designed rather than about call sites that no longer bind.

## 6. N× batch gateway — run a scenario Nx and tally (belongs in play)

Guidance experiments (baseline vs a `SKILL.md` change) are measured by running a
scenario many times and tallying per-run outcomes. The shell scripts in
[`scripts/`](scripts) get us by: `verify-runs.sh` for single-arm verification,
`compare-wordings.sh` for an alternating A/B, `tally.sh` to read accumulated spec runs. They
launch at full concurrency with no stagger, and a wave count has to be chosen by
hand against the session usage limit.

Make it a first-class mechanism in **play** — framework work, not a spec helper or
a shell loop (cf. "Review later: move scene management to play"). Run a named
scenario N times with capped concurrency and return a per-run tally and pass-rate.
Per run, capture the pytest result plus the scenario's signals (skill loaded; the
production shape). This makes experiments (baseline vs B, gateway variants)
reproducible rather than one-off.

The elimination methodology these encode — paired waves, a control arm, stopping
on contamination — is the subject of item 2.

## 7. Contract-test ClaudeCli's options

`ClaudeCli` passes `--permission-mode`, `--session-id`, `--add-dir`, and
`--plugin-dir` to real claude, but only a bare prompt is contract-tested
(`play/tests/contract/test_claude_cli.py`). Add one contract test per option,
verifying it does what we expect against the real CLI, one at a time.

## 8. Capture the effort used in the agent transcript

The versions header records the CLI and the model a run used (ADR
[0017](docs/architecture/decisions/0017-record-cli-version-and-model-in-the-run-transcript.md)),
but not its **reasoning effort**, which bears on a lesson's provenance (ADR
[0015](docs/architecture/decisions/0015-capture-xdd-skill-missteps-as-lessons.md))
the same way.

Since CLI 2.1.212 the effort a run used is observable: every `assistant` event in
the session JSONL carries a top-level `"effort"` field, reading `"high"` on the
pinned model. Read it from there and render it in the versions header beside CLI
and MODEL. TDD in `play` (`claude_transcriber.py`) — extend the current
transcriber rather than waiting on the ground-up rewrite in ADR
[0014](docs/architecture/decisions/0014-separate-claude-jsonl-translation-from-the-transcriber.md).

This records what a run *actually used*, which is a separate matter from choosing
it deliberately — that is §9.

## 9. Pin reasoning effort, and record the context window

ADR [0019](docs/architecture/decisions/0019-pin-and-record-reasoning-effort-and-context-window.md)
(Proposed) was written when neither value could be read back from a run. That no
longer holds for either, so the ADR needs revising before it is acted on. What a
run on 2.1.220 shows:

- **Effort is readable back** — §8 covers capturing it. What is left here is
  *setting* it, rather than taking whatever the CLI defaults to.
- **The context window is readable back too** — new behaviour, observed on
  2.1.220. `claude -p --output-format json` reports it under `modelUsage`, keyed
  by the resolved model: `"claude-opus-5[1m]": {"contextWindow": 1000000,
  "canonicalModel": "claude-opus-5"}`. The session JSONL and the `system/init`
  event still report a bare `claude-opus-5` with no `[1m]` variant, which is
  where the earlier finding came from.
- The harness passes no `--effort`, so runs take the CLI default — measured as
  `high` on the pinned model.

Two pieces of work, each TDD in `play/`:

1. **Pin effort.** Add a `--effort` flag to the harness's `claude -p` invocation
   (`play/src/claude_cli.py`), set to `high` so the flag records behaviour rather
   than changes it.

   Levels are **model-dependent**, so the flag must be **gated on the resolved
   model** — passing `--effort` to a model that does not support it fails the run.
   `ClaudeCli` therefore needs to know which model it is invoking.
2. **Record the context window.** Extend the versions header (ADR 0017) with the
   window the harness asked for, since no run reports it back. **Revisit:** the
   bullet above shows a run does report it, so reading it back may be the better
   source — and would record what the run used rather than what was requested.

Then backfill the captured lessons' metadata from the recorded values rather than
from this investigation.

## 10. Simplify the dev commands with a build tool

The "before any commit" gate — test → lint → mutation — and the levels of test and
check (unit, contract, integration, the spec configs, focused/full mutation, the full
baseline) are currently sequenced by hand and documented as prose in
[COMMANDS.md](COMMANDS.md). In a JVM project this would be a build script (`gradle
build` runs compile → test → checks in one command). Python has no single equivalent,
and `uv` (unlike cargo/gradle) has no built-in task runner. This item explores encoding
the levels and the gate as named tasks. **Choice TBC — this will mature into an ADR
after further discussion.**

### Options considered

- **`poethepoet` (poe)** — tasks in `pyproject.toml` (`[tool.poe.tasks]`), run via
  `uv run poe <task>`. Most native to the uv + pyproject setup, but per-pyproject and
  Python-only, with no natural root to orchestrate across `play`/`spec`/`stagentic-test`.
- **`just`** — a `justfile` of recipes; recipe-with-dependencies gives a task DAG (like
  Gradle's), `just --list` gives discoverability (like `gradle tasks`), and it is
  polyglot. Scoped to this repo, a single **root `justfile`** orchestrating the
  sub-projects through `uv run --directory …` is the cleanest shape — no import/module
  machinery (that was only for cross-repo reuse, which we've decided we don't need).
- **`nox`** (`noxfile.py`) — session-based; only worth it for matrix testing across
  Python versions or dist/build steps. Overkill for chaining checks.

**Current lean: `just`, single root `justfile`.** `poe` is the fallback if we'd rather
keep tasks in `pyproject.toml`.

### Shape (levels as recipes, composites via dependencies)

Illustrative, not exhaustive:

```make
lint: lint-play lint-spec lint-helpers
play-unit:    uv run --directory play pytest -m "not contract and not integration"
play-full:    uv run --directory play pytest
helpers:      uv run --directory stagentic-test pytest
spec:         uv run --directory spec pytest tests
spec-critic:  uv run --directory spec pytest tests --inspector=critic
spec-real:    uv run --directory spec pytest tests --agent=real
mutate module:  uv run --directory play mutmut run '{{module}}*'
mutate-all:     uv run --directory play mutmut run

check: play-unit lint                        # fast, gated
baseline: play-full play-integration helpers spec spec-critic spec-real
build: lint baseline mutate-all              # the gradle-build analogue
```

Recipe dependencies run first and abort on the first failure, so the gate's ordering
comes for free; `just --list` documents the levels.

### The gating, precisely

- **Mutation must follow a green baseline** — correctness, not economy: mutation testing
  measures whether tests kill mutants, so it is meaningless on red.
- **test → lint is fail-fast economy, not a dependency** — linting a red tree isn't
  wrong, just wasted; we fix behaviour before polishing style.
- **Mutation depends on *tests*, not on *lint*** — a lint failure doesn't invalidate
  mutation results; lint sits before mutation only to fail cheap. So: tests gate
  everything; lint and mutation both need green tests but are independent of each other.

### `build` vs the current scoped rules

`gradle build` feels cheap to re-run because Gradle is **incremental and cached** — it
skips work whose inputs didn't change. A `just build` here has none of that: `baseline`
hits **real claude** (spec-critic, spec-real) and `mutate-all` is a full sweep, so a
full `build` is minutes and network-dependent every time. That is exactly why the
current "before any commit" rules in [CLAUDE.md](CLAUDE.md) are **scoped** (single test
file → just that file; play-src change → full baseline) rather than always-everything.

So the real decision is **what runs when**, not the recipe:

- **Fast vs full split** — `check` (lint + unit) for routine commits; `build` (full)
  before significant commits or in CI.
- **Automated git hook vs manual** — the Python `pre-commit` framework can run a task on
  `git commit`, but it must stay **fast** (ruff on staged files, maybe the unit lane);
  the full baseline and mutation must never live in a git hook (every commit would stall
  for minutes and call real claude). So: hook → `check`; `build` stays a task you invoke.
- **Scoped judgement vs always-full** — keep the cheaper scoped rules (a human/agent
  picks scope) or go always-full (simpler, slow, no caching to rescue it).

### What a runner cannot encode

The runner gates a command's exit code; it cannot make the mutation **judgement** — a
survivor means *subtract the speculative code* (or document an accepted-mutation), not
"add a test". That call stays with the human/agent (see
[working-practices](docs/working-practices.md)).

### Open decisions (for the ADR)

1. Tool: `just` (lean) vs `poe`.
2. `baseline` parallelism: it is deliberately parallel today (six suites at once, ≈ one
   scenario's wall-clock); `just` runs dependencies **sequentially**, so a parallel
   `baseline` needs shell `&`/`wait` in that one recipe, or we accept serial.
3. Fast-auto (`pre-commit` hook) + manual full `build`, keep the scoped rules, or a blend.

## 11. Improvement plan working approach

One change at a time: apply it, run the test(s) the change's scope calls
for, then propose a commit — behavioural and structural changes kept in
separate commits (see
[`docs/working-practices.md`](docs/working-practices.md)).

At the start of the review run the full baseline tests and then full mutation test.
If clear, for a file under review, add all lenses in the correct order to 
the task list before reviewing any files. Number each lens in the task list.

Then, once the task list is complete, for each lens, one at a time, review the
file through that lens and:
- Tell me the lens
- If no issues seen through that lens, say no issues (no explanation
  needed) and await the user's approval to proceed to the next lens.
- If changes are required, show me the before and after of the change you
  propose and await the user's approval to proceed.

Review the file *only* when its lens is the active one — and read it fresh at
that moment, along with any other file the lens needs (e.g. the production
source for the execution-flow lens). Do not read the whole file, nor any file
a later lens will need, up front. Each lens is a fresh pass: look at the file
through that lens alone, report, and only then move to the next.

Reading fresh at each lens is correctness, not tidiness. A lens reviews the
file's current state — which includes any change an earlier lens produced. A
read taken before those changes is stale, so a lens reviewing against it is
reviewing text that no longer exists. Re-read when the lens becomes active so
every pass sees what is actually there.

Reporting lens-by-lens in order is necessary but not sufficient — the
examination itself must be lens-at-a-time, not a single up-front sweep
re-narrated as separate lenses.

### Reviewing a test file

Review the file through each lens below in turn, confirming each one by
one — even where it needs no change. Most lenses are the conventions in
[`docs/architecture/conventions/test-conventions.md`](docs/architecture/conventions/test-conventions.md);
the last two are inferred from the reviewed exemplars.
Add each lens to your task list for easy tracking in the session.

Review the file through each lens below in turn and in the order below:

- Whole-story tests
- Test order follows the production code's execution flow
- Tests can be grouped in classes that express key variations in behaviour
- Test naming `test_should_<behaviour>` and each reads in context of its holding class
- MagicMock interrogation forms
- Per-property test layout: relevant kwargs at the top
- Explicit no-raise via `does_not_raise`
- Write parametrise rows with `case`
- Parametrise value-flow tests over ≥2 cases with `ids`
- Don't test Python's own enforcement
- Assertion vocabulary: PyHamcrest matchers
- Pin exact composed output once via `==`
- `spec=Class` vs `spec=Class()` for directly-callable spies
- Stub callable → lambda; spy callable → `MagicMock`
- Marker placement: lane marker on the holding class, not the method (inferred)
- Import grouping: stdlib / third-party / first-party (inferred, ruff-enforced)

### Reviewing a src file

As above, but through these lenses. Most are the conventions in
[`docs/architecture/conventions/src-conventions.md`](docs/architecture/conventions/src-conventions.md);
the last two are inferred from the reviewed exemplars.
Add each lens to your task list for easy tracking in the session.

Review the file through each lens below in turn and in the order below:

- Type hints on every public method parameter (avoid `Any`)
- Required vs optional: no `| None = None` defaults for test convenience
- Runtime guards for semantic preconditions the type system can't express
- Helper-function parameter order mirrors the call it makes
- IDE warning suppression with an inline rationale comment
- Private functions follow the order their calls appear
- Orchestrator methods read at a single level of abstraction
- Naming-suffix vocabulary for private helpers
- Kwarg-style helpers compose into prose at the call site
- Public methods take keyword-only args (`*` separator) (inferred)
- Import grouping: stdlib / third-party / first-party (inferred, ruff-enforced)

## 12. Improvement plan

We are working through each file in turn, bringing each up to the reference
standard set by `critic.py` / `TestCritic` — matching the conventions inferred
from `critic.py` and `test_critic.py` — and running mutation testing to confirm
coverage.

`critic.py` is the current reference standard for this repo's production code.
`TestCritic` is the current reference standard for tests.

For each file:
- Review the test first, then the implementation; bring both to the standard
  set by `critic.py` / `test_critic.py`.
- Match the conventions inferred from those files, alongside the documented
  conventions in `docs/architecture/conventions/`.
- Run mutation testing (`mutmut`, per ADR
  [0010](docs/architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md)):
  review survivors against the tests and act where appropriate. Read-only for now (ADR 0010 stage 1); "where
  appropriate" is judgement, not an enforced gate. `source_paths` grows by one
  file as each reaches acceptable coverage.

The conventions in `docs/architecture/conventions/` are the standard; the
reference-standard files above are exemplars, not infallible. A file under
review may already exceed them in places. Anchor each proposed change on the
convention text and judgement, not on what other files happen to do. Follow
the working practices in [`docs/working-practices.md`](docs/working-practices.md)
for the workflow itself, rather than inferring one from the files.

Some files have a per-file punch list at
`docs/architecture/improvements/<file>.md` — items tracked separately so they
don't bury NEXT.md.

### `play/src/`

- [x] `critic.py` (and `tests/test_critic.py`, `tests/integration/test_critic_integration.py`)
- [x] `agent.py` (and `tests/test_agent.py`)
- [x] `result.py` (and `tests/test_result.py`)
- [x] `result_matchers.py` (and `tests/test_result_matchers.py`)
- [x] `fake_agent.py` (and `tests/test_fake_agent.py`)
- [x] `claude_cli.py` (and `tests/test_claude_cli.py`, `tests/contract/test_claude_cli.py`)
- [x] `claude_session.py` (and `tests/test_claude_session.py`)
- [x] `auditor.py` (and `tests/test_auditor.py`)
- [x] `scorecard_results.py` (and `tests/test_scorecard_results.py`)
- [~] `claude_transcriber.py` (and `tests/test_claude_transcriber.py`) —
  interim mutation coverage added: the `varied-transcript` approval test took
  survivors 75 → 8 (the remaining 8 are equivalence mutants). Bringing it fully
  to standard is superseded by a ground-up rewrite — see ADR
  [0014](docs/architecture/decisions/0014-separate-claude-jsonl-translation-from-the-transcriber.md).
  Kept out of `source_paths` (the equivalence survivors can't be accepted yet).
- [ ] `claude_jsonl_path.py` (and `tests/test_claude_jsonl_path.py`)
- [ ] `failure_message.py` (and `tests/test_failure_message.py`)
- [ ] `raise_when.py` (and `tests/test_raise_when.py`)
- [ ] `scorecard_json_extraction.py` (and `tests/test_scorecard_json_extraction.py`)
- [ ] `archiver.py` (and `tests/test_archiver.py`)
- [ ] `inspector.py` — No test yet

A cross-cutting improvement surfaced by the critic extraction — a
`ScorecardEntry` type spanning `Critic`, `Auditor`, and `formatted_failures_for`
— is deferred and tracked in
[`docs/architecture/improvements/scorecard-entry.md`](docs/architecture/improvements/scorecard-entry.md).

### `spec/`

- [ ] `conftest.py`

### `Auditor.evaluate` should derive per-row status, not hard-code PASS

`Auditor.evaluate`'s success branch hard-codes `"status": "PASS"` for every
result row. It can, because that branch is reached only when `_failures_from`
returns empty — the all-pass case. The literal is a symptom: the Auditor
reimplements pass/fail branching instead of delegating to
`ScorecardResults.failures()` the way `Critic.evaluate` does. On success it
hand-builds an all-PASS `results` list; on any failure it returns `Failure(...)`
and bypasses `ScorecardResults` entirely.

The symmetric fix mirrors `Critic.evaluate`: evaluate each row once into a real
`PASS`/`FAIL` status, build `ScorecardResults(should=should, results=<those
rows>)`, then `match scorecard.failures()`. Then the status is derived per row,
never a literal, and both `evaluate` methods read alike.

This is a **behavioural** change, not a refactor: it changes what
`ScorecardResults.should` holds on the Auditor path (today
`_entries_from(should)`; Critic stores the raw `should`) and the `Failure`
payload shape, so it needs test updates. It is adjacent to the deferred
`ScorecardEntry` work above — do it as its own red-green.

### Error handling (cross-cutting — final review)

A final pass over error handling across the harness, after the per-file
reviews above. `ClaudeSession`, for one, has no error handling and does not
wrap errors raised by `ClaudeCli` — whether it should is a question the
per-file lenses don't currently cover.

**Prerequisite:** the error-handling strategy must be agreed and documented
first. An ADR captures the 'why' and proposes the 'how';
`docs/architecture/conventions/src-conventions.md` hosts the finally agreed
'how'. The review checks each file against the agreed convention, so it
can't run until that convention exists.

A candidate convention to start from — every public entry point to the
`play` framework:
- returns `Success` when it succeeds;
- returns `Failure` for an in-domain failure;
- raises an exception for a mechanical/infrastructure failure (file not
  found, network unavailable).

This may become the standard for all files.

## 13. Heading case — a repo-wide convention question

`SKILL.md` uses title-case headings; every other heading in the repo is sentence
case. Neither [`document-style.md`](docs/document-style.md) nor
[`writing-style.md`](docs/writing-style.md) states a rule, so there is a
convention to adopt rather than one being broken.

`SKILL.md` is agent-facing and its wording is measured, so changing it needs a
fresh measurement. Every other doc is human-facing, where case is unmeasured.

- Document that split in [`document-style.md`](docs/document-style.md).
- Harmonise the repo to one case — a wide diff, no evidence either way.
- Change `SKILL.md` to sentence case, and re-measure.

## 14. Capture the CLI's stdout and stderr in the run artefacts

Nothing records what the `claude` process itself printed. `ClaudeCli` already
captures both streams (`capture_output=True`), but uses `result.stderr` only in
the failure path — on a successful run both are discarded. `transcript.md` is
built by `ClaudeTranscriber` from the session JSONL, which never carries them. So
a run that passes leaves no record of anything the CLI said about it.

Observed on 2.1.220: a hand-built run mirroring a scenario (scene copied to a
temp dir, cwd there, `--settings <copy>/.claude/settings.json`, `--add-dir`)
printed to stderr:

```
Ignoring 1 permissions.allow entry from .claude/settings.json: this workspace
has not been trusted.
```

That one is benign — the handed-over settings still apply, which is ADR
[0016](docs/architecture/decisions/0016-hand-the-agent-its-permissions-as-a-launch-argument.md)'s
whole point, and a real run in the same session ran `uv run pytest` without an
approval. The concern is the class, not the instance: a real scenario run almost
certainly prints the same line, and would equally swallow a warning that mattered
— a skipped MCP server, a demoted plugin, a settings file that failed validation.

One such warning matters directly once 0023 lands. When `--model` names a version
the account cannot use, Claude Code
[substitutes the default at startup](https://code.claude.com/docs/en/model-config#setting-your-model)
and says so on stderr. Discarding stderr means the run proceeds on a model nobody
chose, silently.

Archive both streams beside `transcript.md`, so a run's artefacts carry what the
CLI reported as well as what the agent did. TDD in `play`.

## 15. The versions header reports only the first model a run used

`claude_transcriber.py` returns the first `message.model` it finds in the session
JSONL and stops, so the `[VERSIONS]` header names one model even when a run used
more than one. Two ways that happens:

- **Safety-classifier fallback.** A flagged request re-runs on another model and
  the session continues there —
  [automatic model fallback](https://code.claude.com/docs/en/model-config#automatic-model-fallback)
  sends a cybersecurity-flagged Opus 5 request to Opus 4.8. Remote for a
  miles-to-km converter, but it would not show.
- **Background work.** Claude Code runs conversation summarisation and similar on
  the `haiku` alias —
  [background token usage](https://code.claude.com/docs/en/costs#background-token-usage).
  Spec-run session files carry `ai-title` entries, which record no model at all,
  and `modelUsage` from `--output-format json` showed
  `claude-haiku-4-5-20251001` beside the agent's model in three of four hand-built
  calls. Spec runs never request that output format, so none of it is visible.

ADR 0017 promises the transcript records what a run used. It records what the
first assistant message used. Report every model a run touched, and consider
whether the artefacts should capture `--output-format json` so background usage is
visible at all.

**Why it matters beyond provenance.** A run that switched model part-way through
measures a blend of two models, so its result says nothing about the wording. That
is the same class of problem as the contaminated window ADR 0025 handles, where a
control-arm failure invalidates a wave and the runs are discarded. A switched run
should be discarded the same way — but only detection makes that possible, since a
switched run and a clean one currently produce identical artefacts.

The two classifier paths differ on the pinned model. A cybersecurity-flagged
request re-runs on Opus 4.8 and the session continues there, silently. A
biology-flagged request is refused outright, because Opus 5 runs its own biology
classifiers with no fallback model, so that one shows up as a refusal the critic
grades as a failure. Neither is the wording's fault; only the first is invisible.

No sign of either happening yet: six spec-run session files each used exactly one
model, and the scenarios are about a miles-to-km converter. The risk grows if a
scenario ever touches auth, crypto or input validation.

## Future options

- **Chunk long runs under the session usage limit**: a calibrated wave count,
  optionally stopping on a limit signal (`system/api_retry` surfaced from
  `ClaudeCli`), since there is no scriptable query for remaining budget. Today the
  count is chosen by hand.
- **Critic saves results to a file**: instruct the critic prompt to write
  its scorecard to a specific file (e.g. `scorecard.json`) rather than
  returning JSON in the response text. The file would contain only JSON,
  sidestepping the prose-stripping problem entirely.
- **Mix mechanical and judgement characteristics in one scorecard**:
  the auditor today verifies rows that carry a `verify` lambda; the
  critic today judges rows that carry only prose. A scorecard given
  to the critic could mix both shapes — the critic would judge the
  prose rows and delegate the lambda-bearing rows to the auditor.
  Other routing approaches are possible.

## Known constraints

- **The opening scene carries transient dirs into the agent's workspace.**
  `_set_opening_scene_for` filters only `transcript.md`, so an untracked
  `__pycache__` in a scene dir is copied too — the agent's starting state differs
  between machines. `uv run pytest` then adds `.venv/` and `.pytest_cache/`.
  `Archiver` filters all three, so artefacts show none of it. Should the scene
  copy filter them too?

## Enforcing working-practices via hooks

This began as a way to make the dev process less painful. It became more
than that: a technique we tested and proved, and one that may turn into a
mechanism for building the xdd skill itself.

**What happened.** The working practices live in
`docs/working-practices.md`, and the agent reads them at session start.
Even so, it kept skipping steps — pulled back toward habits from its
training data.

The specific miss: on every green, the agent skipped both the focused
mutation test and the commit. It was too eager to get on to writing the
next test.

**What we decided.** Nudge the agent with a hook at the moment it reaches
green — exactly where the miss happens. A reminder injected into context,
not a block.

It was tested this session and worked: the nudge fired on each green with
a mutation target in flight, and pulled the green step back into view.

**Why it matters beyond the dev process.** The xdd skill's job is to steer
an agent through Red-Green-Refactor. A hook that nudges at green is that
same kind of steering. So what we prove here may carry straight into how
the skill is built — this is learning for the product, not throwaway
scaffolding.

The hooks are still spike code: written quickly, no tests yet. If they
become part of the skill, they get the proper TDD treatment then.

**Why a hook, not just the doc.** A `CLAUDE.md` pointer is advisory — it
needs the agent to read *and* apply the doc, and both have failed
(read-but-not-applied, and applied-as-paraphrase). A hook puts the nudge
in the harness instead of in prose. Scripts live in `.claude/hooks/`;
config in the checked-in `.claude/settings.json`.

The hooks — built, and candidates:

- **SessionStart — inject the docs to be applied literally (built).**
  `session_start_inject_docs.sh` prints the literal text of
  `docs/working-practices.md` and `docs/commit-style.md` into context via
  `hookSpecificOutput.additionalContext` — the actual words, not a pointer,
  because the failure mode was paraphrase, not ignorance. Cannot block. Each
  doc in the list carries its own preamble saying how to apply it.

  Commit style joined the list after a second read-but-not-applied miss: a
  proposal written to an inferred style with the doc unopened. Session start is
  the only trigger that reaches every commit message, because a proposal is
  text rather than a tool call — a prompt hook covers only the messages a
  person asks for, a green hook only those a test precedes, and by `git commit`
  the message is already written. Under propose-on-green, most proposals answer
  no prompt at all.
- **PostToolUse after pytest — green nudge (built, proven this session).**
  On a pytest green, injects a reminder to run the focused mutation check
  (see [Mutation testing](COMMANDS.md#mutation-testing)) on the in-flight
  file before moving on. Cannot block (it runs after the tool); a pure
  reminder. Targets the exact miss:
  moving on from a green without the focused mutation test.
- **PostToolUse after mutmut — marker writer (candidate).** Would detect
  `mutmut run`, parse the result, and write a marker (timestamp +
  clean/dirty) for a commit gate to read.
- **PreToolUse before commit — the gate (candidate).** Would block the
  commit (exit 2 / `permissionDecision: deny`) unless the mutmut marker is
  newer than the most-recently-edited `source_paths` file, and list the
  missing steps.

The marker writer and the gate are ideas, not plans. We build them only if
we see cases where the nudges alone aren't enough.

If we do build the gate, two questions are open:

- **Hard block or soft warn.** A hard block enforces the mechanical check
  but is brittle: a buggy gate blocks good commits, and judgement clauses
  ("a survivor must be a *documented* accepted-mutation") can't be encoded,
  so it would block on survivors it can't judge. Current lean: hard block
  on the mechanical check (mutmut ran clean since the last edit), warn-only
  when survivors are present, leaving judgement to the agent.
- **Matcher robustness.** The scripts parse `tool_input.command`
  themselves rather than trust an `if: Bash(git commit*)` glob, because the
  repo convention is `git -C <repo> commit`, which the naive glob misses.

**Known limits.** A hook sees one command and its args, not the meaning of
the session. String matchers can be dodged by spelling things differently.
Judgement clauses can't be encoded. So the hooks back up the mechanical
steps only — they don't remove the agent's job of applying the doc.

## Review later: consider a delta from scene to scene

Each task's `scene/` is a full copy of the workspace end-state and also the
opening scene for the next task, so consecutive scenes duplicate most files
verbatim — building task 2's scene copies task 1's `pyproject.toml`, tests,
`.claude/settings.json`, and `uv.lock` unchanged, and only `src/conversion.py`
differs.

Consider holding each scene as a delta — only the files that changed from the
previous scene. A full scene is then materialised by copying the scenes in
order, each later scene's files layered over what is already there. This
applies to both roles a scene plays: the start (opening) scene for the next
task, and the reference (end-state) scene the critic judges against.

## Review later: move scene management to play

Scene setup currently lives in the spec test helper `_set_opening_scene_for`
(copying the previous scene into the workspace, filtering the previous task's
outputs like `transcript.md`). Materialising a scene, deciding what carries
into an opening scene, and the delta-from-scene idea above are framework work —
they belong in `play/`, not in a spec test helper. Move scene management into
`play/` so scenarios call it rather than reimplement it.

## Lowest priority: review whether the fake agent and auditor belong in the spec

The `FakeAgent` and `Auditor` were introduced to drive out the design of
`play` — they're framework machinery, and probably aren't useful for
validating the xdd skill itself (that's the real agent + critic's job). They
likely belong as their own example scenarios under `play/tests/`, exercising
`FakeAgent`/`Auditor` as framework features, which would let us remove them
from the xdd spec scenarios. Review whether the spec should run only the real
agent + critic, with the fake/auditor relocated to `play`'s own tests, their
appropriate home.
