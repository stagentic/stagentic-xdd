# Working practices

## Lead with the proposed commit

For any change or series of changes, propose the commit message(s)
before the implementation. See [`commit-style.md`](commit-style.md)
for the shape of commit messages.

For any series of changes, number each proposed commit so the user
can easily reference them. When revisiting a numbered item, always
include at least the commit subject.

Applies to proposals from a person or from an agent.

## Separate behavioural and structural changes

Each commit either changes observable behaviour (new test, new
feature, bug fix) or it changes structure (refactor that preserves
behaviour) — never both. Mixed commits force a reviewer to
disentangle which lines do what; separate commits let each kind be
inspected on its own.

Structural commits may touch a single file or many files. What makes
them structural is that they preserve behaviour: every test passes
before and after, with no test added or modified to assert new
intent.

The rule applies equally to source and tests.

## Mutation-test as you work

Per ADR
[0010](architecture/decisions/0010-adopt-mutation-testing-with-a-staged-rollout.md),
mutation testing is part of doing the work — scoped to the files in
`source_paths`, not the whole codebase.

**During TDD, on green, before committing**, run a focused
`mutmut run "<file>*"` on the file just developed. A surviving mutant means the
implementation did more than the failing test demanded — dial the code back to
only what the test requires, then commit. The pressure is on the
implementation, not the test suite.

**Before work is 'done'**, run the full-set `mutmut run`. It must come back
clean, or every survivor a documented accepted-mutation. Because `source_paths`
holds only files whose coverage is already accepted, this defends those
baselines against regression.
