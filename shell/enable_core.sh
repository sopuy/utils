#!/usr/bin/env bash
# Usage       : source setup_ps1.sh
###############################################################################
:<<-'EOF'
__author__ = "Daning"

Description:
    enable core dump
    copy the script to the directory: /etc/profile.d/
EOF

ulimit -c unlimited 2>/dev/null