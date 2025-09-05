#!/usr/bin/env bash
# Usage       : sh check_ssl_expiration.sh [ usage ]
###############################################################################
:<<-'EOF'
__author__ = "sunhn"

Description:
    check ssl expired day;
    the expiration time is less than 10 days, and then alarm;

deploy: 
    zabbix agent excute script by day;
    deploy according to region;

trigger: 
    zabbix: exclude SSL or include ERROR or WARNING;
    prometheus: < 10

EOF


check_ssl_expiration() {
    local HOST="$1"
    local OUTPUT_FORMAT="${2:-zabbix}"      # Default output format is zabbix
    local WARNING_DAYS="${3:-10}"           # Default warning days is 10


    # Retrieve and parse SSL expiration date
    local EXP_DATE=$(timeout 10s openssl s_client -connect "$HOST" -servername "$HOST" < /dev/null 2>/dev/null | \
        openssl x509 -enddate -noout 2>/dev/null | sed 's/^notAfter=//')
    local EXP_UNIX_TIMESTAMP=$(date -d "$EXP_DATE" +%s 2>/dev/null)
    local CURRENT_UNIX_TIMESTAMP=$(date +%s)

    if [[ -z "$EXP_DATE" || "$EXP_UNIX_TIMESTAMP" -le "$CURRENT_UNIX_TIMESTAMP" ]]; then
        echo "$([[ "$OUTPUT_FORMAT" == "prometheus" ]] && echo "ssl_expiration_days{host=\"$HOST\"} 0" || echo "ERROR: [$HOST] SSL check failed.")"
        return 1
    fi

    local DAYS_LEFT=$(( (EXP_UNIX_TIMESTAMP - CURRENT_UNIX_TIMESTAMP) / 86400 ))
    if [[ "$OUTPUT_FORMAT" == "prometheus" ]]; then
        MON_DATA="ssl_expiration_days{host=\"$HOST\"} $DAYS_LEFT"
        echo -e ${MON_DATA}
        # curl data to pushgateway
        # echo -e ${MON_DATA} | curl --data-binary @- "${PUSHGATEWAY_URL}"
    else
        if [[ "$DAYS_LEFT" -le "$WARNING_DAYS" ]]; then
            echo "WARNING: [$HOST] SSL expires in $DAYS_LEFT days ($EXP_DATE)"
        else
            echo "OK: [$HOST] SSL valid until $EXP_DATE"
        fi
    fi
}

# Check for the required argument
if [ $# -eq 0 ]; then
    echo "Usage: sh check_ssl_expiration.sh [host] [warning_days] [output_format]"
    exit 1
fi

# Call the function with the provided arguments
# check_ssl_expiration "trade.xxx.com:443"
check_ssl_expiration "$1" "$2" "$3"