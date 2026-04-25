#!/usr/bin/env bash

__prompt_shorten_path() {
    local pwd_path="$1"
    if [[ "$pwd_path" == "$HOME" ]]; then
        printf '%s' "~"
        return
    fi
    printf '%s' "$(basename "$pwd_path")"
}

__prompt_user_host() {
    printf '%s' "${USER:-$(whoami)}"
}
