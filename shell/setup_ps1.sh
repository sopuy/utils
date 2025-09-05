#!/usr/bin/env bash
# Usage       : source setup_ps1.sh
###############################################################################
:<<-'EOF'
__author__ = "Daning"

Description:
    1. setup the variable: HOST_NAME
    2. copy the script to the directory: /etc/profile.d/
    ps: you can use ansible set the variable: HOST_NAME and copy the script to the directory: /etc/profile.d/
EOF

COLOR_PRE_RED="\[\033[41;30m\]"
COLOR_PRE_GREEN="\[\033[42;37m\]"
COLOR_SUF="\[\033[0m\]"


# HOST_NAME="uat-hkidc-10.8.8.151"
HOSTNAME_PRE=$(echo ${HOST_NAME} | awk -F "-" '{print $1}')

if [ "$(id -u)" -eq 0 ]; then
  U_ID='#'
else
  U_ID='$'
fi


if [ "$HOSTNAME_PRE" == "uat" ]; then
    PS1="${COLOR_PRE_RED} [\u@${HOST_NAME} \W]${U_ID} ${COLOR_SUF}"
elif [ "$HOSTNAME_PRE" == "prod" ]; then
    PS1="${COLOR_PRE_GREEN} [\u@${HOST_NAME} \W]${U_ID} ${COLOR_SUF}"
fi
