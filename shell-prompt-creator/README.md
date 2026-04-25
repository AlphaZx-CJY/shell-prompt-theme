# Shell Prompt Creator

An agent skill for creating custom Bash/Zsh prompt themes with personalized colors, path display styles, and layout components.

## What It Does

This skill helps you (or your agent) generate a complete, zero-dependency shell prompt theme tailored to your preferences:

- **Color palettes** — cyberpunk, minimal, solarized, dracula, catppuccin, or fully custom
- **Path display** — basename only, truncated, or full path
- **Layout components** — reorder or omit user, path, git branch, tool hints, and arrow
- **Shell support** — Bash, Zsh, or both

## Installation

### Via skills.sh

```bash
npx skills add AlphaZx-CJY/shell-prompt-theme
```

### Manual

Copy the `shell-prompt-creator` directory to your agent's skills folder:

```bash
cp -r shell-prompt-creator ~/.claude/skills/
```

## Usage

Once installed, ask your agent to create a prompt theme for you. Examples:

> "帮我做一个极简的 zsh prompt，只要路径和 git 分支，颜色用灰色调。"

> "I want a cyberpunk bash prompt with full path display and tool hints."

> "Make a minimal prompt with just the current directory and a green arrow."

The agent will guide you through preferences, generate the theme files, and optionally install them.

## Generated Theme Structure

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

## License

MIT
