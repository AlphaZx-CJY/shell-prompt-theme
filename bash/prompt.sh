#!/usr/bin/env bash

PROMPT_THEME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "$PROMPT_THEME_DIR/config.sh"
source "$PROMPT_THEME_DIR/lib/utils.sh"
source "$PROMPT_THEME_DIR/lib/git.sh"
source "$PROMPT_THEME_DIR/lib/tools.sh"

__prompt_last_exit=0

__prompt_color_code() {
    local name="$1"
    case "$name" in
        red) printf '%s' '\[\e[31m\]' ;;
        green) printf '%s' '\[\e[32m\]' ;;
        yellow) printf '%s' '\[\e[33m\]' ;;
        blue) printf '%s' '\[\e[34m\]' ;;
        cyan) printf '%s' '\[\e[36m\]' ;;
        gray) printf '%s' '\[\e[90m\]' ;;
        lightgray) printf '%s' '\[\e[38;5;250m\]' ;;
        brightblue) printf '%s' '\[\e[94m\]' ;;
        lightblue) printf '%s' '\[\e[38;5;110m\]' ;;
        neonpink) printf '%s' '\[\e[38;5;168m\]' ;;
        neoncyan) printf '%s' '\[\e[38;5;73m\]' ;;
        neonpurple) printf '%s' '\[\e[38;5;103m\]' ;;
        neongreen) printf '%s' '\[\e[38;5;72m\]' ;;
        neonred) printf '%s' '\[\e[38;5;167m\]' ;;
        *) printf '%s' '\[\e[0m\]' ;;
    esac
}

__build_prompt() {
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
        local branch="${git_info%|*}"
        local dirty="${git_info#*|}"
        local git_color
        if [[ "$dirty" == "1" ]]; then
            git_color=$(__prompt_color_code "$PROMPT_GIT_DIRTY_COLOR")
        else
            git_color=$(__prompt_color_code "$PROMPT_GIT_CLEAN_COLOR")
        fi
        git_part=" ${git_color}(${branch})${reset}"
    fi

    local tools_info
    tools_info=$(__prompt_build_tools_info)
    local tools_part=""
    if [[ -n "$tools_info" ]]; then
        local tools_color
        tools_color=$(__prompt_color_code "$PROMPT_TOOLS_COLOR")
        tools_part=" ${tools_color}${tools_info}${reset}"
    fi

    local arrow_color
    if [[ $exit_code -eq 0 ]]; then
        arrow_color=$(__prompt_color_code "$PROMPT_SUCCESS_COLOR")
    else
        arrow_color=$(__prompt_color_code "$PROMPT_FAILURE_COLOR")
    fi

    local time_str
    time_str=$(date '+%H:%M')
    local time_color
    time_color=$(__prompt_color_code "$PROMPT_TIME_COLOR")

    PS1="${reset}\[\e[22m\]${user_color}${user_host}${reset} ${pwd_color}${pwd_part}${reset}${git_part}${tools_part} ${arrow_color}➜${reset} ${time_color}${time_str}${reset} "
}

PROMPT_COMMAND='__build_prompt'
