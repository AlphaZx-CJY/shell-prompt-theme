# Shell Prompt Theme

A minimal, clean shell prompt theme for Bash and Zsh with smart git branch display and optional development toolchain hints.

## Preview

```
user ~/.../shell-prompt-theme (main) ➜
```

With tool hints:
```
user ~/.../shell-prompt-theme (main) [py:3.11|node:20.5] ➜
```

Command failed:
```
user ~/.../shell-prompt-theme (main) ✗
```

## Features

- Git branch — auto-shows when inside a git repo, hidden otherwise. Color indicates clean (cyan) or dirty (yellow) state.
- Arrow prompt — `➜` in cyan when last command succeeded, `✗` in red when it failed.
- Toolchain hints — optionally display active Python virtualenv, Node.js, Rust, Go, or Docker context.
- Zero dependencies — no Oh-My-Zsh, no Nerd Fonts, no external packages.

## Quick Start

```bash
# Install for both bash and zsh
./install.sh --all

# Or selectively
./install.sh --bash
./install.sh --zsh
```

Then reload your shell or run:

```bash
source ~/.bashrc   # or
source ~/.zshrc
```

## Configuration

Edit `config.sh` to customize behavior:

```bash
# Choose which tools to display
# "auto" | "none" | comma-separated list like "py,node,go"
PROMPT_TOOLS="auto"

# Always show tool versions even without project files
PROMPT_TOOLS_ALWAYS_SHOW=0

# Color settings (red, green, yellow, blue, cyan, gray, lightblue)
PROMPT_USER_COLOR="yellow"
PROMPT_PATH_COLOR="lightblue"
PROMPT_TOOLS_COLOR="gray"
PROMPT_GIT_CLEAN_COLOR="cyan"
PROMPT_GIT_DIRTY_COLOR="yellow"
PROMPT_SUCCESS_COLOR="cyan"
PROMPT_FAILURE_COLOR="red"
```

### Supported Tool Identifiers

| Identifier | Display example | Trigger condition |
|-----------|-----------------|-------------------|
| `py` / `python` | `py:myenv` or `py:3.11` | `VIRTUAL_ENV` / `CONDA_DEFAULT_ENV` active, or project files present |
| `node` / `js` | `node:20.5` | `package.json` or `.nvmrc` present |
| `rs` / `rust` | `rs:1.75` | `Cargo.toml` present |
| `go` | `go:1.21` | `go.mod` present |
| `docker` | `docker` | `Dockerfile` / `docker-compose.yml` / `compose.yml` present |

## Uninstall

```bash
./install.sh --uninstall
```

## Repository

Remote repository: https://github.com/AlphaZx-CJY/shell-prompt-theme.git
