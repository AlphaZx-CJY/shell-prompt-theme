#!/usr/bin/env bash

__prompt_in_project() {
    local files=("$@")
    for f in "${files[@]}"; do
        if [[ -f "$f" ]]; then
            return 0
        fi
    done
    return 1
}

__prompt_tool_python() {
    local in_project=0
    if __prompt_in_project "requirements.txt" "pyproject.toml" "setup.py" "setup.cfg" "Pipfile"; then
        in_project=1
    fi

    if [[ -n "$VIRTUAL_ENV" ]]; then
        local venv_name
        venv_name=$(basename "$VIRTUAL_ENV")
        printf 'py:%s' "$venv_name"
        return 0
    fi

    if [[ -n "$CONDA_DEFAULT_ENV" && "$CONDA_DEFAULT_ENV" != "base" ]]; then
        printf 'py:%s' "$CONDA_DEFAULT_ENV"
        return 0
    fi

    if [[ "$PROMPT_TOOLS_ALWAYS_SHOW" == "1" || "$in_project" == 1 ]]; then
        local py_version
        py_version=$(python --version 2>&1 | awk '{print $2}')
        if [[ -n "$py_version" ]]; then
            printf 'py:%s' "$py_version"
            return 0
        fi
    fi

    return 1
}

__prompt_tool_node() {
    local in_project=0
    if __prompt_in_project "package.json" ".nvmrc"; then
        in_project=1
    fi

    if [[ "$PROMPT_TOOLS_ALWAYS_SHOW" == "1" || "$in_project" == 1 ]]; then
        local node_version
        node_version=$(node --version 2>/dev/null)
        if [[ -n "$node_version" ]]; then
            node_version="${node_version#v}"
            printf 'node:%s' "$node_version"
            return 0
        fi
    fi

    return 1
}

__prompt_tool_rust() {
    local in_project=0
    if __prompt_in_project "Cargo.toml"; then
        in_project=1
    fi

    if [[ "$PROMPT_TOOLS_ALWAYS_SHOW" == "1" || "$in_project" == 1 ]]; then
        local rust_version
        rust_version=$(rustc --version 2>/dev/null | awk '{print $2}')
        if [[ -n "$rust_version" ]]; then
            printf 'rs:%s' "$rust_version"
            return 0
        fi
    fi

    return 1
}

__prompt_tool_go() {
    local in_project=0
    if __prompt_in_project "go.mod"; then
        in_project=1
    fi

    if [[ "$PROMPT_TOOLS_ALWAYS_SHOW" == "1" || "$in_project" == 1 ]]; then
        local go_version
        go_version=$(go version 2>/dev/null | awk '{print $3}')
        if [[ -n "$go_version" ]]; then
            go_version="${go_version#go}"
            printf 'go:%s' "$go_version"
            return 0
        fi
    fi

    return 1
}

__prompt_tool_docker() {
    if __prompt_in_project "Dockerfile" "docker-compose.yml" "docker-compose.yaml" "compose.yml" "compose.yaml"; then
        printf 'docker'
        return 0
    fi

    if [[ "$PROMPT_TOOLS_ALWAYS_SHOW" == "1" ]]; then
        if command -v docker &>/dev/null; then
            printf 'docker'
            return 0
        fi
    fi

    return 1
}

__prompt_build_tools_info() {
    if [[ "$PROMPT_TOOLS" == "none" ]]; then
        echo ""
        return 0
    fi

    local check_py=0 check_node=0 check_rust=0 check_go=0 check_docker=0

    if [[ "$PROMPT_TOOLS" == "auto" || -z "$PROMPT_TOOLS" ]]; then
        check_py=1
        check_node=1
        check_rust=1
        check_go=1
        check_docker=1
    else
        local tools_list="${PROMPT_TOOLS//,/ }"
        for t in $tools_list; do
            case "$t" in
                python | py) check_py=1 ;;
                node | js) check_node=1 ;;
                rust | rs) check_rust=1 ;;
                go) check_go=1 ;;
                docker) check_docker=1 ;;
            esac
        done
    fi

    local tools=()
    local out

    if [[ "$check_py" == 1 ]]; then
        out=$(__prompt_tool_python)
        [[ -n "$out" ]] && tools+=("$out")
    fi
    if [[ "$check_node" == 1 ]]; then
        out=$(__prompt_tool_node)
        [[ -n "$out" ]] && tools+=("$out")
    fi
    if [[ "$check_rust" == 1 ]]; then
        out=$(__prompt_tool_rust)
        [[ -n "$out" ]] && tools+=("$out")
    fi
    if [[ "$check_go" == 1 ]]; then
        out=$(__prompt_tool_go)
        [[ -n "$out" ]] && tools+=("$out")
    fi
    if [[ "$check_docker" == 1 ]]; then
        out=$(__prompt_tool_docker)
        [[ -n "$out" ]] && tools+=("$out")
    fi

    if [[ ${#tools[@]} -gt 0 ]]; then
        local IFS="|"
        printf '[%s]' "${tools[*]}"
    else
        echo ""
    fi
}
