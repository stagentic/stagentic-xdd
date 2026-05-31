# Documentation style

In-repo docs (READMEs, ADRs, CLAUDE.md, etc.) describe the system as it stands now. Do not narrate transitions from earlier states — phrases like *"no longer needs X"*, *"used to depend on Y"*, *"X has been removed"* do not belong in current-state prose. New readers land on the current version with no knowledge of prior states; transition language is meaningful only to someone reading the git log.

Ask: *"would this sentence make sense to a reader who has never seen any previous version of this file?"* If a clause references a previous state to contextualise the current one, delete it — the current state stands on its own.

Docs must be environment-agnostic. Describe mechanisms in terms of files, commands, and Claude Code features — never in terms of a specific environment (containers, host OS, install method, directory layout, etc.). A reader on any setup should find the docs accurate.

See `docs/writing-style.md` for label-agnostic framing rules (do not reach for "BDD-flavoured", "Gherkin-style", etc.) and the discipline of quoting actual stated reasons in commit bodies and ADRs.
