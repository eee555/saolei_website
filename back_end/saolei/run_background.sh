#!/bin/bash
set -eu

service_name="$1"
start_delay="$2"
nice_value="$3"
child_pid=not-started

log_exit() {
    exit_status=$?
    signal_name=none
    if [ "$exit_status" -gt 128 ]; then
        signal_name=$(kill -l "$((exit_status - 128))" 2>/dev/null) || signal_name=unknown
    fi
    printf '%s service=%s pid=%s exit_status=%s signal=%s\n' \
        "$(date -Is)" "$service_name" "$child_pid" "$exit_status" "$signal_name"
}
trap log_exit EXIT

case "$service_name" in
    apscheduler)
        set -- python3 -u -X faulthandler manage.py runapscheduler
        ;;
    db-worker)
        set -- python3 -u -X faulthandler manage.py db_worker_robust --interval "${4:-2}"
        ;;
    *)
        printf 'Unknown background service: %s\n' "$service_name" >&2
        exit 2
        ;;
esac

printf '%s service=%s launcher_pid=%s start_delay=%s\n' \
    "$(date -Is)" "$service_name" "$$" "$start_delay"
sleep "$start_delay"

if command -v ionice >/dev/null 2>&1; then
    set -- ionice -c2 -n7 "$@"
fi
nice -n "$nice_value" "$@" &
child_pid=$!
printf '%s service=%s pid=%s started\n' "$(date -Is)" "$service_name" "$child_pid"
wait "$child_pid"
