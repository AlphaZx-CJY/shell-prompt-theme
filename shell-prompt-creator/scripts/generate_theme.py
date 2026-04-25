#!/usr/bin/env python3
"""
Generate a shell prompt theme from a configuration dict.
Usage:
    python generate_theme.py <output-dir> <config.json>
"""

import json
import os
import sys
from pathlib import Path

# --- templates ---

CONFIG_SH_TEMPLATE = """#!/usr/bin/env bash
# {theme_name} - Shell Prompt Theme Configuration

PROMPT_TOOLS="{tools_mode}"
PROMPT_TOOLS_ALWAYS_SHOW={tools_always_show}
PROMPT_PATH_STYLE="{path_style}"
PROMPT_PATH_COLOR="{path_color}"
PROMPT_USER_COLOR="{user_color}"
PROMPT_TOOLS_COLOR="{tools_color}"
PROMPT_GIT_CLEAN_COLOR="{git_clean_color}"
PROMPT_GIT_DIRTY_COLOR="{git_dirty_color}"
PROMPT_SUCCESS_COLOR="{success_color}"
PROMPT_FAILURE_COLOR="{failure_color}"
"""

UTILS_SH = r'''#!/usr/bin/env bash
__prompt_shorten_path() {
    local pwd_path="$1"
    case "$PROMPT_PATH_STYLE" in
        basename)
            if [[ "$pwd_path" == "$HOME" ]]; then
                printf '%s' "~"
                return
            fi
            printf '%s' "$(basename "$pwd_path")"
            ;;
        full)
            if [[ "$pwd_path" == "$HOME"* ]]; then
                printf '%s' "~${pwd_path#$HOME}"
            else
                printf '%s' "$pwd_path"
            fi
            ;;
        short)
            local p="${pwd_path/#$HOME/~}"
            local IFS=/
            local -a parts=($p)
            local result=""
            local len=${#parts[@]}
            for ((i=0; i<len-1; i++)); do
                result="${result}${parts[i]:0:1}/"
            done
            result="${result}${parts[len-1]}"
            printf '%s' "$result"
            ;;
        *)
            printf '%s' "$pwd_path"
            ;;
    esac
}

__prompt_user_host() {
    printf '%s' "${USER:-$(whoami)}"
}
'''

GIT_SH = r'''#!/usr/bin/env bash
__prompt_git_info() {
    local branch
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git describe --tags --exact-match 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    [[ -z "$branch" ]] && return
    local dirty=0
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        dirty=1
    fi
    printf '%s' "${branch}|${dirty}"
}
'''

TOOLS_SH = r'''#!/usr/bin/env bash
__prompt_build_tools_info() {
    local tools=""
    local enabled="$PROMPT_TOOLS"
    [[ "$enabled" == "none" ]] && return
    [[ "$enabled" == "auto" ]] && enabled="py,node,rs,go,docker"
    IFS=',' read -ra TOOL_LIST <<< "$enabled"
    for t in "${TOOL_LIST[@]}"; do
        case "$t" in
            py|python)
                if [[ -n "$VIRTUAL_ENV" ]]; then
                    local venv="$(basename "$VIRTUAL_ENV")"
                    tools="${tools}py:${venv}|"
                elif [[ -n "$CONDA_DEFAULT_ENV" ]]; then
                    tools="${tools}py:${CONDA_DEFAULT_ENV}|"
                elif [[ -f "pyproject.toml" || -f "requirements.txt" || -f "setup.py" ]]; then
                    local pyver="$(python3 --version 2>/dev/null | awk '{print $2}')"
                    [[ -n "$pyver" ]] && tools="${tools}py:${pyver}|"
                fi
                ;;
            node|js)
                if [[ -f "package.json" || -f ".nvmrc" ]]; then
                    local nodever="$(node --version 2>/dev/null | tr -d 'v')"
                    [[ -n "$nodever" ]] && tools="${tools}node:${nodever}|"
                fi
                ;;
            rs|rust)
                if [[ -f "Cargo.toml" ]]; then
                    local rustcver="$(rustc --version 2>/dev/null | awk '{print $2}')"
                    [[ -n "$rustcver" ]] && tools="${tools}rs:${rustcver}|"
                fi
                ;;
            go)
                if [[ -f "go.mod" ]]; then
                    local gover="$(go version 2>/dev/null | awk '{print $3}' | tr -d 'go')"
                    [[ -n "$gover" ]] && tools="${tools}go:${gover}|"
                fi
                ;;
            docker)
                if [[ -f "Dockerfile" || -f "docker-compose.yml" || -f "compose.yml" ]]; then
                    tools="${tools}docker|"
                fi
                ;;
        esac
    done
    tools="${tools%|}"
    [[ -n "$tools" ]] && printf '%s' "[${tools//|/|}]"
}
'''

BASH_COLOR_MAP = {
    "red": r"'\[\e[31m\]'",
    "green": r"'\[\e[32m\]'",
    "yellow": r"'\[\e[33m\]'",
    "blue": r"'\[\e[34m\]'",
    "cyan": r"'\[\e[36m\]'",
    "gray": r"'\[\e[90m\]'",
    "lightgray": r"'\[\e[38;5;250m\]'",
    "brightblue": r"'\[\e[94m\]'",
    "lightblue": r"'\[\e[38;5;110m\]'",
    "neonpink": r"'\[\e[38;5;168m\]'",
    "neoncyan": r"'\[\e[38;5;73m\]'",
    "neonpurple": r"'\[\e[38;5;103m\]'",
    "neongreen": r"'\[\e[38;5;72m\]'",
    "neonred": r"'\[\e[38;5;167m\]'",
}

ZSH_COLOR_MAP = {
    "red": r"'%F{red}'",
    "green": r"'%F{green}'",
    "yellow": r"'%F{yellow}'",
    "blue": r"'%F{blue}'",
    "cyan": r"'%F{cyan}'",
    "gray": r"'%F{gray}'",
    "lightgray": r"'%F{250}'",
    "brightblue": r"'%F{39}'",
    "lightblue": r"'%F{110}'",
    "neonpink": r"'%F{168}'",
    "neoncyan": r"'%F{73}'",
    "neonpurple": r"'%F{103}'",
    "neongreen": r"'%F{72}'",
    "neonred": r"'%F{167}'",
}


def _color_case_bash(name: str) -> str:
    if name in BASH_COLOR_MAP:
        return f"        {name}) printf '%s' {BASH_COLOR_MAP[name]} ;;"
    # numeric 256-color
    if name.isdigit():
        return f"        {name}) printf '%s' '\\[\\e[38;5;{name}m\\]' ;;"
    return f"        {name}) printf '%s' '\\[\\e[0m\\]' ;;"


def _color_case_zsh(name: str) -> str:
    if name in ZSH_COLOR_MAP:
        return f"        {name}) printf '%s' {ZSH_COLOR_MAP[name]} ;;"
    if name.isdigit():
        return f"        {name}) printf '%s' '%F{{{name}}}' ;;"
    return f"        {name}) printf '%s' '%f' ;;"


def generate_bash_prompt(colors_used: set, layout: list, arrow: str, fail_arrow: str) -> str:
    cases = "\n".join(_color_case_bash(c) for c in sorted(colors_used))
    # Build segments
    segments = []
    for seg in layout:
        if seg == "user":
            segments.append(r'${user_color}${user_host}${reset}')
        elif seg == "path":
            segments.append(r'${pwd_color}${pwd_part}${reset}')
        elif seg == "git":
            segments.append(r'${git_part}')
        elif seg == "tools":
            segments.append(r'${tools_part}')
    segments.append(r'${arrow_color}' + arrow + r'${reset}')

    ps1 = " ".join(segments)

    return rf'''#!/usr/bin/env bash

PROMPT_THEME_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"

source "$PROMPT_THEME_DIR/config.sh"
source "$PROMPT_THEME_DIR/lib/utils.sh"
source "$PROMPT_THEME_DIR/lib/git.sh"
source "$PROMPT_THEME_DIR/lib/tools.sh"

__prompt_last_exit=0

__prompt_color_code() {{
    local name="$1"
    case "$name" in
{cases}
        *) printf '%s' '\[\e[0m\]' ;;
    esac
}}

__build_prompt() {{
    local exit_code=$?
    __prompt_last_exit=$exit_code

    local reset='\[\e[0m\]'

    local user_host
    user_host=$(__prompt_user_host)
    local user_color
    user_color=$(__prompt_color_code "$PROMPT_USER_COLOR")

    local pwd_part
    pwd_part=$(__prompt_shorten_path "$PWD")
    local pwd_color
    pwd_color=$(__prompt_color_code "$PROMPT_PATH_COLOR")

    local git_info
    git_info=$(__prompt_git_info)

    local git_part=""
    if [[ -n "$git_info" ]]; then
        local branch="${{git_info%|*}}"
        local dirty="${{git_info#*|}}"
        local git_color
        if [[ "$dirty" == "1" ]]; then
            git_color=$(__prompt_color_code "$PROMPT_GIT_DIRTY_COLOR")
        else
            git_color=$(__prompt_color_code "$PROMPT_GIT_CLEAN_COLOR")
        fi
        git_part=" ${{git_color}}(${{branch}})${{reset}}"
    fi

    local tools_info
    tools_info=$(__prompt_build_tools_info)
    local tools_part=""
    if [[ -n "$tools_info" ]]; then
        local tools_color
        tools_color=$(__prompt_color_code "$PROMPT_TOOLS_COLOR")
        tools_part=" ${{tools_color}}${{tools_info}}${{reset}}"
    fi

    local arrow_color
    if [[ $exit_code -eq 0 ]]; then
        arrow_color=$(__prompt_color_code "$PROMPT_SUCCESS_COLOR")
    else
        arrow_color=$(__prompt_color_code "$PROMPT_FAILURE_COLOR")
    fi

    PS1="${{reset}}\[\e[22m\]{ps1} "
}}

PROMPT_COMMAND='__build_prompt'
'''


def generate_zsh_prompt(colors_used: set, layout: list, arrow: str, fail_arrow: str) -> str:
    cases = "\n".join(_color_case_zsh(c) for c in sorted(colors_used))
    segments = []
    for seg in layout:
        if seg == "user":
            segments.append(r'${user_color}${user_host}${reset}')
        elif seg == "path":
            segments.append(r'${pwd_color}${pwd_part}${reset}')
        elif seg == "git":
            segments.append(r'${git_part}')
        elif seg == "tools":
            segments.append(r'${tools_part}')
    segments.append(r'${arrow_color}' + arrow + r'${reset}')

    prompt = " ".join(segments)

    return rf'''#!/usr/bin/env zsh

PROMPT_THEME_DIR="$(cd "$(dirname "${{(%):-%x}}")/.." && pwd)"

source "$PROMPT_THEME_DIR/config.sh"
source "$PROMPT_THEME_DIR/lib/utils.sh"
source "$PROMPT_THEME_DIR/lib/git.sh"
source "$PROMPT_THEME_DIR/lib/tools.sh"

__prompt_last_exit=0

__prompt_zcolor() {{
    local name="$1"
    case "$name" in
{cases}
        *) printf '%s' '%f' ;;
    esac
}}

__zbuild_prompt() {{
    local exit_code=$?
    __prompt_last_exit=$exit_code

    local reset='%f'

    local user_host
    user_host=$(__prompt_user_host)
    local user_color
    user_color=$(__prompt_zcolor "$PROMPT_USER_COLOR")

    local pwd_part
    pwd_part=$(__prompt_shorten_path "$PWD")
    local pwd_color
    pwd_color=$(__prompt_zcolor "$PROMPT_PATH_COLOR")

    local git_info
    git_info=$(__prompt_git_info)

    local git_part=""
    if [[ -n "$git_info" ]]; then
        local branch="${{git_info%|*}}"
        local dirty="${{git_info#*|}}"
        local git_color
        if [[ "$dirty" == "1" ]]; then
            git_color=$(__prompt_zcolor "$PROMPT_GIT_DIRTY_COLOR")
        else
            git_color=$(__prompt_zcolor "$PROMPT_GIT_CLEAN_COLOR")
        fi
        git_part=" ${{git_color}}(${{branch}})${{reset}}"
    fi

    local tools_info
    tools_info=$(__prompt_build_tools_info)
    local tools_part=""
    if [[ -n "$tools_info" ]]; then
        local tools_color
        tools_color=$(__prompt_zcolor "$PROMPT_TOOLS_COLOR")
        tools_part=" ${{tools_color}}${{tools_info}}${{reset}}"
    fi

    local arrow_color
    if [[ $exit_code -eq 0 ]]; then
        arrow_color=$(__prompt_zcolor "$PROMPT_SUCCESS_COLOR")
    else
        arrow_color=$(__prompt_zcolor "$PROMPT_FAILURE_COLOR")
    fi

    PROMPT="%f%b{prompt} "
}}

autoload -Uz add-zsh-hook
add-zsh-hook precmd __zbuild_prompt
'''


INSTALL_SH = r'''#!/usr/bin/env bash
set -e

THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_bash() {
    local rc="$HOME/.bashrc"
    local line="source '$THEME_DIR/bash/prompt.sh'"
    if grep -qF "$line" "$rc" 2>/dev/null; then
        echo "Already installed in ~/.bashrc"
    else
        echo "$line" >> "$rc"
        echo "Installed for Bash (~/.bashrc)"
    fi
}

install_zsh() {
    local rc="$HOME/.zshrc"
    local line="source '$THEME_DIR/zsh/prompt.sh'"
    if grep -qF "$line" "$rc" 2>/dev/null; then
        echo "Already installed in ~/.zshrc"
    else
        echo "$line" >> "$rc"
        echo "Installed for Zsh (~/.zshrc)"
    fi
}

uninstall() {
    local rc
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        [[ -f "$rc" ]] || continue
        sed -i.bak "/source .*\/bash\/prompt.sh/d" "$rc" 2>/dev/null || true
        sed -i.bak "/source .*\/zsh\/prompt.sh/d" "$rc" 2>/dev/null || true
        rm -f "$rc.bak"
    done
    echo "Uninstalled. Please restart your shell."
}

case "${1:-}" in
    --bash) install_bash ;;
    --zsh) install_zsh ;;
    --all) install_bash; install_zsh ;;
    --uninstall) uninstall ;;
    *)
        echo "Usage: $0 [--bash|--zsh|--all|--uninstall]"
        exit 1
        ;;
esac
'''


def generate(config: dict, out_dir: Path):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bash").mkdir(exist_ok=True)
    (out_dir / "zsh").mkdir(exist_ok=True)
    (out_dir / "lib").mkdir(exist_ok=True)

    # Collect colors used
    colors_used = set()
    for k in ["path_color", "user_color", "tools_color", "git_clean_color",
              "git_dirty_color", "success_color", "failure_color"]:
        colors_used.add(config.get(k, "cyan"))

    layout = config.get("layout", ["user", "path", "git", "tools", "arrow"])
    arrow = config.get("arrow", "➜")
    fail_arrow = config.get("fail_arrow", "✗")

    # Write files
    (out_dir / "config.sh").write_text(
        CONFIG_SH_TEMPLATE.format(
            theme_name=config.get("name", "my-prompt"),
            tools_mode=config.get("tools_mode", "auto"),
            tools_always_show=int(config.get("tools_always_show", False)),
            path_style=config.get("path_style", "basename"),
            path_color=config.get("path_color", "neoncyan"),
            user_color=config.get("user_color", "neonpink"),
            tools_color=config.get("tools_color", "neonpurple"),
            git_clean_color=config.get("git_clean_color", "neongreen"),
            git_dirty_color=config.get("git_dirty_color", "neonpink"),
            success_color=config.get("success_color", "neoncyan"),
            failure_color=config.get("failure_color", "neonred"),
        ), encoding="utf-8"
    )

    (out_dir / "lib" / "utils.sh").write_text(UTILS_SH, encoding="utf-8")
    (out_dir / "lib" / "git.sh").write_text(GIT_SH, encoding="utf-8")
    (out_dir / "lib" / "tools.sh").write_text(TOOLS_SH, encoding="utf-8")
    (out_dir / "bash" / "prompt.sh").write_text(
        generate_bash_prompt(colors_used, layout, arrow, fail_arrow), encoding="utf-8"
    )
    (out_dir / "zsh" / "prompt.sh").write_text(
        generate_zsh_prompt(colors_used, layout, arrow, fail_arrow), encoding="utf-8"
    )
    (out_dir / "install.sh").write_text(INSTALL_SH, encoding="utf-8")
    os.chmod(out_dir / "install.sh", 0o755)

    print(f"Generated theme at: {out_dir}")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <output-dir> <config.json>")
        sys.exit(1)

    out_dir = Path(sys.argv[1])
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        config = json.load(f)

    generate(config, out_dir)


if __name__ == "__main__":
    main()
