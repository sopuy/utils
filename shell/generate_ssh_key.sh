#!/usr/bin/env bash
# Usage       : bash generate_ssh_key.sh [ usage ]
###############################################################################
:<<-'EOF'
__author__ = "Ace"

Description:
    Usage: ./generate_ssh_key.sh <key_name> [<algorithm>]
    Default algorithm is ed25519.
    对 rsa / dsa 来说，加 -o 很有用，否则可能生成旧格式的私钥。
    -t rsa -b 4096 -o
EOF

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <key_name> [<algorithm>]" >&2
    exit 1
fi

# Parameters
KEY_NAME="$1"
ALGORITHM="${2:-ed25519}"


# Check if file already exists
if [[ -e "$KEY_NAME" || -e "$KEY_NAME.pub" ]]; then
    echo "Error: Key file '$KEY_NAME' already exists." >&2
    exit 1
fi

# Generate SSH key
if ssh-keygen -t "$ALGORITHM" -a 100 -f "$KEY_NAME" -N ""; then
    echo "SSH key '$KEY_NAME' created successfully using algorithm '$ALGORITHM'."
else
    echo "Failed to create SSH key." >&2
    exit 1
fi