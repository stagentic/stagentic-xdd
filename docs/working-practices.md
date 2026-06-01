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
