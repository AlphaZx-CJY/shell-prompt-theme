# AGENTS.md — Shell Prompt Theme

> This file contains project-specific context for AI coding agents.
> The reader is assumed to know nothing about this project.

---

## Project Overview

This is a **minimal shell prompt theme** for Bash and Zsh. It displays:

- The current working directory (shortened, with `~` for `$HOME`).
- Git branch name when inside a git repository, with color indicating clean (default cyan) or dirty (default yellow) state.
- Optional development toolchain hints (Python, Node.js, Rust, Go, Docker).
- A colored arrow (`➜` on success, `✗` on failure) reflecting the last command's exit code.

It has **zero dependencies** — no Oh-My-Zsh, no Nerd Fonts, no external packages. It is implemented entirely in POSIX-compatible shell scripts sourced by the user's shell.

---

## Project Structure

```
.
├── bash/prompt.sh      # Bash-specific prompt hook and color handling
├── zsh/prompt.sh       # Zsh-specific prompt hook and color handling
├── lib/
│   ├── git.sh          # Git branch and dirty-state detection
│   ├── tools.sh        # Toolchain hint builders (py, node, rust, go, docker)
│   └── utils.sh        # Shared utilities (path shortening)
├── config.sh           # User-facing configuration variables and defaults
├── install.sh          # Installer / uninstaller script
└── README.md           # Human-facing documentation
```

- **`bash/prompt.sh`** and **`zsh/prompt.sh`** are the shell-specific entry points. They source `config.sh` and the `lib/*.sh` modules, then register a prompt-building function with the shell's precmd hook (`PROMPT_COMMAND` for Bash, `add-zsh-hook precmd` for Zsh).
- **`lib/`** contains shared logic used by both shells. All functions are prefixed with `__prompt_` to avoid polluting the user's shell namespace.
- **`config.sh`** holds user-customizable variables (colors, tool display mode). It is sourced by both shell entry points.
- **`install.sh`** appends or removes `source` lines from `~/.bashrc` and `~/.zshrc`.

---

## Technology Stack

- **Language:** Bash / Zsh shell scripting.
- **Dependencies:** None. Only standard Unix utilities (`git`, `grep`, `sed`, `awk`, `basename`, `dirname`, `printf`, `command -v`).
- **Package Manager:** None. This is not a Node.js, Python, Rust, or other package-based project.
- **Build System:** None. There is no compilation or bundling step.

---

## Build and Test Commands

There is **no build process** and **no test suite** currently. To validate changes:

1. **Source the relevant prompt file directly in a live shell:**
   ```bash
   source bash/prompt.sh   # For Bash
   source zsh/prompt.sh    # For Zsh
   ```
2. **Exercise the prompt:** `cd` into git repositories, create dirty working trees, activate Python virtualenvs, etc., and visually inspect the prompt output.
3. **Check for syntax errors:**
   ```bash
   bash -n bash/prompt.sh install.sh lib/*.sh config.sh
   ```
   (Zsh files can be checked with `zsh -n zsh/prompt.sh` if Zsh is installed.)

---

## Code Style Guidelines

- **Shebang:** All files use `#!/usr/bin/env bash`, even those sourced by Zsh, for consistency and because the code is written to be Bash-compatible.
- **Function naming:** All library and internal functions MUST be prefixed with `__prompt_` (double underscore) to avoid clashing with user-defined functions or other shell plugins.
- **Variables:** Prefer `local` inside functions. Global state is kept to a minimum (`__prompt_last_exit`, `PROMPT_THEME_DIR`).
- **Error suppression:** External command failures (e.g., `git rev-parse`, `node --version`) are silenced with `2>/dev/null` to prevent polluting the terminal.
- **Color abstraction:** Each shell entry point defines its own color-code helper (`__prompt_color_code` for Bash, `__prompt_zcolor` for Zsh) because the escape sequences differ (`\[\e[31m\]` vs `%F{red}`).
- **Path handling:** The shared `__prompt_shorten_path` converts `$HOME` prefixes to `~`.
- **No `set -e` in sourced files:** `set -e` is used only in `install.sh` (a standalone script), never in files that are sourced into an interactive shell, to avoid breaking the user's session.

---

## Configuration

`config.sh` defines the following user-customizable variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPT_TOOLS` | `"auto"` | `"auto"` \| `"none"` \| comma-separated list (e.g., `"py,node,go"`) |
| `PROMPT_TOOLS_ALWAYS_SHOW` | `0` | If `1`, always display tool versions even without project marker files |
| `PROMPT_GIT_CLEAN_COLOR` | `"cyan"` | Color for clean git branch |
| `PROMPT_GIT_DIRTY_COLOR` | `"yellow"` | Color for dirty git branch |
| `PROMPT_SUCCESS_COLOR` | `"cyan"` | Color for success arrow |
| `PROMPT_FAILURE_COLOR` | `"red"` | Color for failure arrow |

Supported tool identifiers in `PROMPT_TOOLS`: `py`/`python`, `node`/`js`, `rs`/`rust`, `go`, `docker`.

---

## Testing Instructions

Because there is no automated test framework, manual verification is required:

1. **Git behavior:**
   - Enter a clean git repo → branch shown in clean color.
   - Modify a tracked file → branch shown in dirty color.
   - Leave the repo → git section disappears.
2. **Tool hints:**
   - Create a `package.json` → `node:<version>` should appear.
   - Create a `Cargo.toml` → `rs:<version>` should appear.
   - Activate a Python virtualenv → `py:<venv_name>` should appear.
3. **Exit code arrow:**
   - Run `true` → arrow is success color.
   - Run `false` → arrow changes to failure color (`✗`).
4. **Cross-shell:** Verify both Bash and Zsh entry points behave identically.

---

## Deployment / Installation

The project is deployed by sourcing the shell-specific entry point from the user's rc file.

- **Install:** `./install.sh [--bash | --zsh | --all]` appends a `source` line to `~/.bashrc` and/or `~/.zshrc`.
- **Uninstall:** `./install.sh --uninstall` removes the `source` line and the associated comment block.
- The installer is idempotent: running it twice does not duplicate entries.
- After installation, the user must reload their shell or run `source ~/.bashrc` / `source ~/.zshrc`.

---

## Security Considerations

- **Do not execute arbitrary commands in the prompt building path.** The current implementation only runs well-known, version-checking commands (`python --version`, `node --version`, `rustc --version`, `go version`).
- **Avoid evaluating untrusted data.** Git branch names and directory paths are printed literally via `printf '%s'`; they are not passed to `eval`.
- **Installer writes to `~/.bashrc` and `~/.zshrc`.** The installer uses `grep -vF` and `sed` to modify these files. It creates a `.tmp` backup during uninstall and a `.bak` during sed cleanup. Ensure these operations are safe and do not corrupt user configuration.
- **No secrets or credentials** are handled by this project.

---

## Key Design Decisions

- **Shared `lib/` with shell-specific wrappers:** The core logic (`git.sh`, `tools.sh`, `utils.sh`) is shared. Only color codes and hook registration differ between Bash and Zsh.
- **Tool detection is project-aware:** Tool versions are shown only when a relevant project marker file is present (e.g., `package.json` for Node), unless `PROMPT_TOOLS_ALWAYS_SHOW=1`.
- **Silent failure everywhere:** Every external command that might fail (e.g., `git` outside a repo, `node` not installed) is silently ignored so the prompt never breaks.
