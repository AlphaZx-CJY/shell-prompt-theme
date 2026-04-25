#!/usr/bin/env bash

__prompt_git_info() {
    local git_branch
    git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [[ -z "$git_branch" ]]; then
        return 1
    fi

    local dirty="0"
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        dirty="1"
    fi

    printf '%s|%s' "$git_branch" "$dirty"
}
