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

    local last1=$(basename "$pwd_path")
    local dir1=$(dirname "$pwd_path")
    local last2=$(basename "$dir1")
    local dir2=$(dirname "$dir1")

    if [[ "$dir2" == "." || "$dir2" == "/" || "$dir2" == "~" ]]; then
        printf '%s' "$pwd_path"
        return
    fi

    if [[ "$pwd_path" == /* ]]; then
        printf '%s' ".../$last2/$last1"
    else
        printf '%s' "${pwd_path%%/*}/.../$last2/$last1"
    fi
}

__prompt_user_host() {
    printf '%s' "${USER:-$(whoami)}"
}
