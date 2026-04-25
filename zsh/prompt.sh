#!/usr/bin/env zsh

PROMPT_THEME_DIR="$(cd "$(dirname "${(%):-%x}")/.." && pwd)"

source "$PROMPT_THEME_DIR/config.sh"
source "$PROMPT_THEME_DIR/lib/utils.sh"
source "$PROMPT_THEME_DIR/lib/git.sh"
source "$PROMPT_THEME_DIR/lib/tools.sh"

__prompt_last_exit=0

__prompt_zcolor() {
    local name="$1"
    case "$name" in
        red) printf '%s' '%F{red}' ;;
        green) printf '%s' '%F{green}' ;;
        yellow) printf '%s' '%F{yellow}' ;;
        blue) printf '%s' '%F{blue}' ;;
        cyan) printf '%s' '%F{cyan}' ;;
        gray) printf '%s' '%F{gray}' ;;
        lightgray) printf '%s' '%F{250}' ;;
        brightblue) printf '%s' '%F{39}' ;;
        lightblue) printf '%s' '%F{110}' ;;
        neonpink) printf '%s' '%F{168}' ;;
        neoncyan) printf '%s' '%F{73}' ;;
        neonpurple) printf '%s' '%F{103}' ;;
        neongreen) printf '%s' '%F{72}' ;;
        neonred) printf '%s' '%F{167}' ;;
        *) printf '%s' '%f' ;;
    esac
}

__zbuild_prompt() {
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
        local branch="${git_info%|*}"
        local dirty="${git_info#*|}"
        local git_color
        if [[ "$dirty" == "1" ]]; then
            git_color=$(__prompt_zcolor "$PROMPT_GIT_DIRTY_COLOR")
        else
            git_color=$(__prompt_zcolor "$PROMPT_GIT_CLEAN_COLOR")
        fi
        git_part=" ${git_color}(${branch})${reset}"
    fi

    local tools_info
    tools_info=$(__prompt_build_tools_info)
    local tools_part=""
    if [[ -n "$tools_info" ]]; then
        local tools_color
        tools_color=$(__prompt_zcolor "$PROMPT_TOOLS_COLOR")
        tools_part=" ${tools_color}${tools_info}${reset}"
    fi

    local arrow_color
    if [[ $exit_code -eq 0 ]]; then
        arrow_color=$(__prompt_zcolor "$PROMPT_SUCCESS_COLOR")
    else
        arrow_color=$(__prompt_zcolor "$PROMPT_FAILURE_COLOR")
    fi

    PROMPT="%f%b${user_color}${user_host}${reset} ${pwd_color}${pwd_part}${reset}${git_part}${tools_part} ${arrow_color}➜${reset} "
}

autoload -Uz add-zsh-hook
add-zsh-hook precmd __zbuild_prompt
