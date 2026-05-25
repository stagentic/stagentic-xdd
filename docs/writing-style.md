# Writing style

Conventions for prose produced by anyone contributing to this repository — commit messages, ADRs, doc text, comments. `CLAUDE.md` covers the basics (subject format, motivation-first bodies, the "what's true after this commit" framing). This document carries the rules that are easier to miss.

## Label-agnostic framing

The project deliberately treats T/B/X-DD as interchangeable labels for the same working practice. The plugin name ("XDD") is itself the agnostic framing; the essay [What almost everyone gets wrong about TDD/BDD](https://open.substack.com/pub/antonymarcano/p/what-almost-everyone-gets-wrong-about-c05) makes the case.

When describing readability, scorecard shape, scenario phrasing, etc., do not reach for "BDD-flavoured", "Given/When/Then", "Gherkin-style", "TDD-style", or similar as the framing. Picking one of those labels reintroduces the label-tribalism the project is trying to leave behind.

**Reach for the underlying property instead.** "Reads at the level of intent", "reads as plain English", "declarative", "call-site readability" — these are the right shape. "Inner-loop" and "outer-loop" are project vocabulary and fine to use.

Exception: when the topic is *specifically* about BDD or TDD as a methodology (e.g. an ADR comparing approaches), the label is the subject and may be named.

## Quote the actual stated reason

When drafting a commit body, ADR, or doc on behalf of someone else — typically an AI agent writing for a human contributor, but the rule applies generally — use the contributor's actual stated reason, not a more abstract or "smarter-sounding" reformulation.

A higher-level framing may also be true, but substituting it changes the historical record of why the decision was actually made. The wrong "why" is worse than a thin "why" — readers can trust a thin record; they cannot tell a polished record from a misleading one.

**Symptom to watch for:** reaching for "architectural" or "principled" framings the contributor did not give. Stop. Either ask whether that framing is also intended, or stick to what was said.
