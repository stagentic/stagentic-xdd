# Trailing hard break — result

**Question:** the reduced skill was measured with two trailing spaces in it. Does
it still hold without them?

**Answer:** yes. 400 of 400 critiques passed.

## Why this was measured at all

The line ablation left the framing sentence ending in two spaces — a markdown hard
break. A blank line already follows it, so the break renders nothing. It was in the
file only because that file is the one the ablation measured, and the wording
adopted is the wording that was run.

Removing it looks free, and the temptation is to treat whitespace as beneath
measurement. It is not: the skill body reaches the model as tokens, and changing
the bytes changes the token stream. "It cannot possibly matter" is a prediction,
and the working practice is that a guidance change is gated by a run rather than by
a prediction. So the strip was gated like any other edit to a measured file.

## What was run

A single arm — `verify-runs.sh --stop-on-fail` over the live working tree, with no
file swapping and no control arm. The question is whether the wording holds, not
which of two wordings is better. An A/B is what a failure would have earned; it is
not what confirming a hold requires.

| | |
|---|---|
| Date | 2026-08-21 to 2026-08-22 |
| CLI | claude 2.1.220 |
| Model | claude-opus-5 |
| Runs | 200 |
| Critiques | 400 |
| Artefacts | `spec/.artefacts/20260821-trailing-hard-break/` |

Snapshot: [`SKILL-no-hard-break.md`](SKILL-no-hard-break.md).

## Result

Cumulative, halting at the first failing batch — it never halted.

| runs | critiques | passed | failed |
|---|---|---|---|
| 100 | 200 | 200 | 0 |
| 200 | 400 | 400 | 0 |

Skill-load confirmed 400/400 two independent ways. The two hundreds ran about
nineteen hours apart into the same set, so the result does not rest on one window.

## What the numbers say

**The strip costs nothing measurable.** The reduced skill with the hard break
passed 400 of 400 in the line ablation; the same file without it passes 400 of
400 here. The two are equal at the same sample size.

## Limits

- **400 of 400 is not proof of zero.** The true failure rate could be as high as
  about 0.75% — roughly 1 in 130 — and still show none.
- **A single arm cannot show the hard break was doing nothing.** It shows the file
  without it holds. The comparison against the line ablation is across separate
  runs, not a paired A/B.
