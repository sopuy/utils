#!/usr/bin/env bash
# Usage       : source log_functions.sh && log_info "This is an info message."
###############################################################################
:<<-'EOF'
__author__ = "Daning"

Description:
    log functions for shell

.%3N ms
.%6N µs
.%9N ns

other scripts can use this function:
source log_functions.sh

Usage:
# The log and log_ function outputs to the console by default and can be redirected to a log file;
log_debug "This is a debug message."
log_info "This is an info message."
log_warning "This is a warning message."
log_error "This is an error message."
log_fatal "This is a fatal message."

# The default log file for the logger function is $HOME/default.log, otherwise it is $LOGGER_FILE;
logger d "This is a debug message."
logger "This is an info message."
logger w "This is a warning message."
logger e "This is an error message."

EOF

log() {
    local log_level=${1:-INFO}
    shift
    local log_message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S.%3N")
    local file_line="$(basename "${BASH_SOURCE[1]}"):${BASH_LINENO[1]}"
    echo "[$timestamp] [$log_level] [$file_line] - $log_message"
}

log_debug() {
    log "DEBUG" "$@"
}
log_info() {
    log "INFO" "$@"
}
log_warning() {
    log "WARNING" "$@"
}
log_error() {
    log "ERROR" "$@"
}
log_fatal() {
    log "FATAL" "$@"
}


logger() {
    local log_level="INFO"
    local log_file="$HOME/default.log"  # Default log file path

    case "$1" in
        d) log_level="DEBUG"; shift ;;
        w) log_level="WARNING"; shift ;;
        e) log_level="ERROR"; shift ;;
        f) log_level="FATAL"; shift ;;
        *) log_level="INFO" ;;
    esac

    # Check if LOGGER_FILE environment variable is set
    if [[ -n "$LOGGER_FILE" ]]; then
        log_file="$LOGGER_FILE"
    fi

    if [[ -n "$log_file" ]]; then
        log "$log_level" "$@" | tee -a "$log_file"
    else
        log "$log_level" "$@"
    fi

}
