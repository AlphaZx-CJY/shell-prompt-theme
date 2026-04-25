#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RC_BASH="$HOME/.bashrc"
RC_ZSH="$HOME/.zshrc"

usage() {
    cat <<EOF
Usage: $0 [--bash | --zsh | --all | --uninstall]

Options:
  --bash       Install for Bash only
  --zsh        Install for Zsh only
  --all        Install for both Bash and Zsh (default)
  --uninstall  Remove from rc files
EOF
    exit 1
}

__install_rc() {
    local rc_file="$1"
    local source_line="$2"

    if [[ ! -f "$rc_file" ]]; then
        echo "Skipped: $rc_file not found"
        return
    fi

    if grep -qF "$source_line" "$rc_file"; then
        echo "Already installed in $rc_file"
    else
        printf '\n# Shell Prompt Theme\n%s\n' "$source_line" >> "$rc_file"
        echo "Installed to $rc_file"
    fi
}

__uninstall_rc() {
    local rc_file="$1"
    local source_line="$2"

    if [[ ! -f "$rc_file" ]]; then
        echo "Skipped: $rc_file not found"
        return
    fi

    if grep -qF "$source_line" "$rc_file"; then
        grep -vF "$source_line" "$rc_file" > "$rc_file.tmp" && mv "$rc_file.tmp" "$rc_file"
        sed -i.bak '/^# Shell Prompt Theme$/d' "$rc_file" && rm -f "$rc_file.bak"
        echo "Uninstalled from $rc_file"
    else
        echo "Not found in $rc_file"
    fi
}

install_bash() {
    local line="source \"$SCRIPT_DIR/bash/prompt.sh\""
    __install_rc "$RC_BASH" "$line"
}

install_zsh() {
    local line="source \"$SCRIPT_DIR/zsh/prompt.sh\""
    __install_rc "$RC_ZSH" "$line"
}

uninstall() {
    local line_bash="source \"$SCRIPT_DIR/bash/prompt.sh\""
    local line_zsh="source \"$SCRIPT_DIR/zsh/prompt.sh\""
    __uninstall_rc "$RC_BASH" "$line_bash"
    __uninstall_rc "$RC_ZSH" "$line_zsh"
}

case "${1:---all}" in
    --bash)
        install_bash
        ;;
    --zsh)
        install_zsh
        ;;
    --all)
        install_bash
        install_zsh
        ;;
    --uninstall)
        uninstall
        ;;
    *)
        usage
        ;;
esac
