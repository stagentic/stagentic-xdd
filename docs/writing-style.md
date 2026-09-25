# Writing style

Conventions for prose produced by anyone contributing to this repository — commit messages, ADRs, doc text, comments. `docs/commit-style.md` covers the commit basics (subject format, motivation-first bodies, the "what's true after this commit" framing). This document carries the rules that are easier to miss.

## Label-agnostic framing

The project deliberately treats T/B/X-DD as interchangeable labels for the same working practice. The plugin name ("XDD") is itself the agnostic framing; the essay [What almost everyone gets wrong about TDD/BDD](https://open.substack.com/pub/antonymarcano/p/what-almost-everyone-gets-wrong-about-c05) makes the case.

When describing readability, scorecard shape, scenario phrasing, etc., do not reach for "BDD-flavoured", "Given/When/Then", "Gherkin-style", "TDD-style", or similar as the framing. Picking one of those labels reintroduces the label-tribalism the project is trying to leave behind.

**Reach for the underlying property instead.** "Reads at the level of intent", "reads as plain English", "declarative", "call-site readability" — these are the right shape. "Inner-loop" and "outer-loop" are project vocabulary and fine to use.

Exception: when the topic is *specifically* about BDD or TDD as a methodology (e.g. an ADR comparing approaches), the label is the subject and may be named.

## Quote the actual stated reason

When drafting a commit body, ADR, or doc on behalf of someone else — typically an AI agent writing for a human contributor, but the rule applies generally — use the contributor's actual stated reason, not a more abstract or "smarter-sounding" reformulation.

A higher-level framing may also be true, but substituting it changes the historical record of why the decision was actually made. The wrong "why" is worse than a thin "why" — readers can trust a thin record; they cannot tell a polished record from a misleading one.

**Symptom to watch for:** reaching for "architectural" or "principled" framings the contributor did not give. Stop. Either ask whether that framing is also intended, or stick to what was said.

## Name the thing

Abstraction hides in small words. "Settings kept here do not reach it", "where a contributor meets it", "the harness is given nothing of its own" — each reads as fine to whoever just wrote it, because they still hold the referent in their head. A reader does not.

Write the noun. If a sentence leans on "here", "it", or "that" to carry its meaning, and the referent is more than a few words back, name it instead.

The same goes for shorthand nouns. Coining "the pin" for "the pinned version" saves three syllables and costs every reader a translation. Use the plain name, even where repeating it feels laboured.

**Symptom to watch for:** re-reading your own sentence to work out what a pronoun refers to. If you have to, the reader will fail.

## Simplify the claim, don't change it

When a sentence is too abstract, say the same thing in plainer words. Do not say a different, easier thing.

Replacing "where a contributor meets it before running anything" with "above the sections that tell you how to run anything" trades an abstract sentence for a concrete but *different* claim — one about page layout rather than about when the reader sees the version. The abstraction was the problem; the meaning was not.

**Symptom to watch for:** the plainer version asserts a fact the original did not.

## A reference must name what it references

"As explained above" points at everything, so it points at nothing. Name the fact being leaned on: *"which the Context above shows does not check for updates"*.

A definite article makes the same kind of promise. "*The* incident" tells the reader they have already met it. An edit that removes the introduction breaks that promise silently — the sentence still reads well, and now refers to nothing.

**Symptom to watch for:** "the" in front of a noun this document has not used yet.
