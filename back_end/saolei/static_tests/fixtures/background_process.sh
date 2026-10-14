#!/bin/bash
nice() { shift 2; "$@"; }
ionice() { shift 2; "$@"; }
python3() {
    printf 'python_args:'
    printf ' <%s>' "$@"
    printf '\n'
    case "$BACKGROUND_TEST_MODE" in
        success) exit 0 ;;
        failure) exit 7 ;;
        killed) kill -KILL "$BASHPID" ;;
        hangup) kill -HUP "$BASHPID"; printf 'survived_hangup\n'; exit 0 ;;
    esac
}
export -f nice ionice python3
nohup bash "$1" "$2" 0 0 2.5
