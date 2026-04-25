#!/usr/bin/env bash

__prompt_shorten_path() {
    local pwd_path="$1"
    if [[ "$pwd_path" == "$HOME" ]]; then
        printf '%s' "~"
        return
    fi
    if [[ "$pwd_path" == "$HOME"/* ]]; then
        pwd_path="~${pwd_path#$HOME}"
    fi
    printf '%s' "$pwd_path"
}

__prompt_user_host() {
    printf '%s' "${USER:-$(whoami)}"
}
