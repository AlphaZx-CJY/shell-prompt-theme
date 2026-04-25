#!/usr/bin/env bash

__prompt_shorten_path() {
    local pwd_path="$1"
    if [[ "$pwd_path" == "$HOME" ]]; then
        echo "~"
        return
    fi
    if [[ "$pwd_path" == "$HOME"/* ]]; then
        pwd_path="~${pwd_path#$HOME}"
    fi
    echo "$pwd_path"
}

__prompt_user_host() {
    local user="${USER:-$(whoami)}"
    local host="${HOSTNAME:-$(hostname -s)}"
    printf '%s@%s' "$user" "$host"
}
