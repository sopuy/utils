#!/usr/bin/env bash
# Usage       : source setup_ps1.sh
###############################################################################
:<<-'EOF'
__author__ = "Daning"

Description:
    setup history time format
    copy the script to the directory: /etc/profile.d/
EOF


export HISTTIMEFORMAT="%F %T "
