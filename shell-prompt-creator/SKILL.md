---
name: shell-prompt-creator
description: >
  Help users create a custom Bash/Zsh prompt theme with personalized colors,
  path display styles, and layout components. Use this skill whenever the user
  mentions beautifying bashrc or zshrc, customizing shell prompt, terminal color
  schemes, command-line themes, or wants a personalized PS1/PROMPT. Also trigger
  when the user asks for a minimal prompt, a git-aware prompt, a cyberpunk or
  neon terminal style, or any kind of shell environment customization.
---

# Shell Prompt Creator

Create bespoke, zero-dependency shell prompt themes for Bash and Zsh.

## When to Use This Skill

Use this skill when the user wants to:

- Customize their shell prompt (PS1 / PROMPT)
- Beautify `~/.bashrc` or `~/.zshrc`
- Change terminal colors, path display, or prompt symbols
- Create a minimal, git-aware, or toolchain-aware prompt
- Build a cyberpunk / neon / pastel / monochrome terminal theme
- Add or remove prompt components (user, host, path, git branch, tool hints, timestamps)

## Workflow

### 1. Discover Preferences

Interview the user to capture their desired style. Ask about:

**Color palette**
- Preset themes: `cyberpunk` (soft neon), `minimal` (grayscale), `solarized`, `dracula`, `catppuccin`, `custom`
- If custom, collect their preferred colors for: user, path, git-clean, git-dirty, success arrow, failure arrow

**Path display style**
- `basename` — only the current directory name (e.g. `lib`)
- `short` — truncated deep paths (e.g. `~/p/s/theme`)
- `full` — full working directory (e.g. `/Users/alpha/projects/shell-prompt-theme`)
- `home` — full path with `~` substitution

**Layout & components**
- Components to include and their order: `[user] [path] [git] [tools] [arrow]`
- Arrow symbol: `➜` (default), `❯`, `→`, `$`, `>`, or custom
- Failure symbol: `✗` (default), `✖`, `✕`, or custom
- Whether to show: username, hostname, git branch, dirty flag, tool hints (py/node/go/rust/docker)

**Shell support**
- Bash only, Zsh only, or both

### 2. Generate Theme Files

Produce a complete, self-contained theme directory:

```
<theme-name>/
├── bash/prompt.sh
├── zsh/prompt.sh
├── lib/
│   ├── git.sh
│   ├── tools.sh
│   └── utils.sh
├── config.sh
├── install.sh
└── README.md
```

**File rules:**
- `config.sh` — All user-facing configuration variables and color defaults.
- `lib/utils.sh` — Path shortening and user/host info utilities.
- `lib/git.sh` — Git branch detection and dirty-state checking.
- `lib/tools.sh` — Development toolchain hints (Python, Node, Rust, Go, Docker).
- `bash/prompt.sh` — Bash-specific prompt builder using `PROMPT_COMMAND`.
- `zsh/prompt.sh` — Zsh-specific prompt builder using `add-zsh-hook precmd`.
- `install.sh` — Appends source lines to `~/.bashrc` and/or `~/.zshrc`.
- `README.md` — Preview examples, configuration guide, and uninstall instructions.

**Critical implementation rules:**
- Use `printf '%s'` (never `echo`) in color helpers and utilities to avoid newline pollution in PS1/PROMPT.
- Prefix Bash PS1 with `\[\e[0m\]\[\e[22m\]` and Zsh PROMPT with `%f%b` to reset attributes and prevent tab-completion bold artifacts.
- Map custom color names to both Bash escapes (`\[\e[38;5;NNm\]`) and Zsh formats (`%F{NN}`).
- Keep the theme zero-dependency: no Oh-My-Zsh, no Nerd Fonts, no external packages.

### 3. Preview

Show the user:
- The generated file tree
- Key code snippets (especially `config.sh` and preview examples)
- Expected prompt appearance in ASCII / code block

### 4. Optional Installation

If the user confirms, run `./install.sh --bash`, `./install.sh --zsh`, or `./install.sh --all`.

If the user wants to install manually, instruct them to:
```bash
source ~/.bashrc   # or
source ~/.zshrc
```

## Color Reference

Standard names and their mappings (add both Bash and Zsh variants):

| Name | Bash | Zsh |
|------|------|-----|
| red | `\[\e[31m\]` | `%F{red}` |
| green | `\[\e[32m\]` | `%F{green}` |
| yellow | `\[\e[33m\]` | `%F{yellow}` |
| blue | `\[\e[34m\]` | `%F{blue}` |
| cyan | `\[\e[36m\]` | `%F{cyan}` |
| gray | `\[\e[90m\]` | `%F{gray}` |
| lightgray | `\[\e[38;5;250m\]` | `%F{250}` |
| brightblue | `\[\e[94m\]` | `%F{39}` |
| lightblue | `\[\e[38;5;110m\]` | `%F{110}` |
| neonpink | `\[\e[38;5;168m\]` | `%F{168}` |
| neoncyan | `\[\e[38;5;73m\]` | `%F{73}` |
| neonpurple | `\[\e[38;5;103m\]` | `%F{103}` |
| neongreen | `\[\e[38;5;72m\]` | `%F{72}` |
| neonred | `\[\e[38;5;167m\]` | `%F{167}` |

Users can also request any 256-color index directly (e.g. `142`).

## Preset Palettes

### cyberpunk (soft)
- `neonpink` (168) — user
- `neoncyan` (73) — path / success
- `neonpurple` (103) — tools
- `neongreen` (72) — git clean
- `neonred` (167) — git dirty / failure

### minimal
- `lightgray` (250) — user / path
- `gray` (90) — git / tools
- `cyan` — success
- `red` — failure

## Path Display Reference

Implement these helpers in `lib/utils.sh`:

```bash
__prompt_shorten_path() {
    local pwd_path="$1"
    case "$PROMPT_PATH_STYLE" in
        basename)
            [[ "$pwd_path" == "$HOME" ]] && printf '%s' "~" || printf '%s' "$(basename "$pwd_path")"
            ;;
        full)
            [[ "$pwd_path" == "$HOME"* ]] && printf '%s' "~${pwd_path#$HOME}" || printf '%s' "$pwd_path"
            ;;
        short)
            # Truncate intermediate dirs to first letter, keep basename
            # e.g. /Users/alpha/projects/shell-prompt-theme -> ~/a/p/shell-prompt-theme
            ;;
    esac
}
```

## Component Reference

Available prompt segments (rendered left-to-right):

1. **user** — Colored username (`$USER`)
2. **host** — Hostname (optional, usually omitted for minimal themes)
3. **path** — Current directory (style configurable)
4. **git** — Branch name in parentheses, color indicates clean/dirty
5. **tools** — Active toolchain hints in brackets: `[py:3.11|node:20.5]`
6. **arrow** — `➜` on success, `✗` on failure (symbols configurable)

Users can reorder these or omit any segment. Default order: `user path git tools arrow`.

## Example Interaction

**User:** "帮我做一个极简的 zsh prompt，只要显示路径和 git 分支，颜色用灰色调。"

**Skill actions:**
1. Set palette: `PROMPT_PATH_COLOR="lightgray"`, `PROMPT_GIT_CLEAN_COLOR="gray"`, `PROMPT_GIT_DIRTY_COLOR="red"`, `PROMPT_SUCCESS_COLOR="lightgray"`, `PROMPT_FAILURE_COLOR="red"`
2. Hide user/tools: set layout to `path git arrow`
3. Generate files for Zsh (and optionally Bash)
4. Show preview:
   ```
   shell-prompt-theme (main) ➜
   ```
5. Ask if they want to install
