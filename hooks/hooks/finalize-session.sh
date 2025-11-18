#!/bin/bash

# finalize-session.sh - Finalizes agent session
# Implements stop hook

# Read JSON input from stdin
input=$(cat)

status=$(echo "$input" | jq -r '.status // empty')
loop_count=$(echo "$input" | jq -r '.loop_count // 0')
conversation_id=$(echo "$input" | jq -r '.conversation_id // empty')

# Log session end
log_file="$HOME/.cursor/hooks/sessions.log"
mkdir -p "$(dirname "$log_file")"

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$timestamp] [SESSION] Conversation: $conversation_id | Status: $status | Loop count: $loop_count" >> "$log_file"

# No follow-up message (can be customized)
cat << EOF
{}
EOF

