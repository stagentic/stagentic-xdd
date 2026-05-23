---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

# 0006 — Use the Claude Code native installer for the pinned CLI version

**Status:** Proposed

## Context

[ADR 0002](0002-pin-claude-code-cli-version.md) pins the Claude Code CLI version and treats bumps as deliberate migrations. It is silent on *how* the pin is installed — the Prerequisites section in `README.md` currently shows two paths:

```
claude install <version>          # for contributors who already have the CLI
npm install -g @anthropic-ai/claude-code@<version>   # for first-time install
```

The official Claude Code documentation now leads with the **native installer** as the recommended path and presents npm as an alternative:

```
curl -fsSL https://claude.ai/install.sh | bash -s <version>     # macOS, Linux, WSL
irm https://claude.ai/install.ps1 | iex                         # Windows PowerShell
```

The native installer supports version pinning via the trailing argument (e.g. `bash -s 2.1.150`) and also accepts a release channel (`bash -s stable`). It installs the CLI as a self-contained binary under the user's home directory (typically `~/.local/bin`) rather than as a global npm package.

This raises a question ADR 0002 did not answer: when the README tells a new contributor how to install the pinned version for the first time, which mechanism should it recommend? And, by extension, which mechanism should the project's build environments use?

### Forces

- **Follow official guidance.** The native installer is now the documented recommended path. Contributors arriving from upstream docs will expect to use it. Diverging from the recommended path needs a reason.
- **Pinning still works.** The native installer accepts an exact version argument, so the ADR 0002 pinning model is unaffected by the choice of installer.
- **Node-free install.** The native installer drops a self-contained binary; it does not require Node.js to be present. The npm path requires Node 18+.
- **PATH wiring.** The native installer places the binary under the user's home directory (`~/.local/bin` on Linux/macOS). A globally-resolvable `claude` command depends on that directory being on `PATH`. `npm install -g` places the binary in a directory that is conventionally already on `PATH` for users who already have global npm packages set up.
- **Existing build environments.** Build environments that run scenarios against the pinned CLI may already have Node.js available for other reasons (e.g. for other JS-based tooling). In such environments, `npm install -g` adds nothing new; in environments without Node.js, the native installer avoids a Node dependency just to install the CLI.
- **Sudo footgun on npm.** The official docs explicitly warn against `sudo npm install -g`. The native installer sidesteps this category of mistake by installing into the user's home directory.

## Decision

Use the **native installer** as the canonical mechanism for installing the pinned CLI version. Specifically:

1. **`README.md` Prerequisites — first-time install.** Replace the `npm install -g @anthropic-ai/claude-code@<version>` line with the native-installer command pinned to the same version:

   ```
   curl -fsSL https://claude.ai/install.sh | bash -s <version>      # macOS, Linux, WSL
   irm https://claude.ai/install.ps1 | iex                          # Windows PowerShell
   ```

   Note next to the Windows command that contributors should pin the version using whatever argument the installer's PowerShell variant supports, and verify before relying on it.

2. **`README.md` Prerequisites — already-installed switch.** Keep the `claude install <version>` line unchanged. It is provided by the CLI itself and works regardless of how the CLI was first installed.

3. **Build environments that install the CLI from scratch.** Use the native installer rather than `npm install -g`. Where the build environment puts the binary at a location that is not already on `PATH`, wire it in explicitly (e.g. by symlinking into a `PATH` directory or by extending `PATH`).

4. **Pin format unchanged.** The version string is still the source of truth recorded in `README.md` per ADR 0002. The installer command is the *mechanism*; the version is the *pin*.

## Consequences

- New contributors see the docs-recommended install path in the README, with no Node.js prerequisite for installing the CLI itself.
- The npm-based install path is no longer the documented default, though it remains officially supported upstream and could be reinstated as a fallback if a future native-installer issue forces it.
- Build environments using the native installer pick up the binary at a non-standard path and must ensure it is resolvable — a small one-time configuration cost per environment.
- The Windows PowerShell variant of the native installer is documented without a clear version-pinning argument; contributors on Windows may need to verify the pinning syntax separately, or fall back to the npm path until that gap is closed.
- Bumping the pin remains a one-line change in `README.md` plus matching updates wherever the version appears in build environments — no change to the ADR 0002 migration workflow.

## Alternatives considered

- **Stay on npm everywhere.** Lower friction in environments that already have Node.js, and avoids the PATH-wiring step. Rejected as the documented default: official docs now lead with the native installer, and following the recommended path is the conservative choice for a project whose reproducibility depends on the CLI surface.
- **Native installer in the README, npm in build environments.** Splits the mechanism along contributor/build lines. Rejected as needlessly divergent: build environments and contributor machines should run the CLI installed the same way to minimise behavioural drift between them.
- **`mise` / `asdf` or a similar version manager.** Provides exact pinning across multiple tools and a uniform install workflow. Rejected (for now) as out of scope: the project pins one CLI, not a tool matrix, and ADR 0002 deliberately avoided introducing a lockfile or version manager just to pin one binary.
