#!/bin/bash

# audit-shell.sh - Audits shell commands executed by Cursor agent
# Implements beforeShellExecution hook

# Read JSON input from stdin
input=$(cat)

# Extract command and working directory
command=$(echo "$input" | jq -r '.command // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')
conversation_id=$(echo "$input" | jq -r '.conversation_id // empty')
generation_id=$(echo "$input" | jq -r '.generation_id // empty')

# Create timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Log to audit file
log_file="$HOME/.cursor/hooks/audit.log"
mkdir -p "$(dirname "$log_file")"
echo "[$timestamp] [SHELL] Conversation: $conversation_id | Generation: $generation_id | CWD: $cwd | Command: $command" >> "$log_file"

# Allow the command (can be modified to block specific commands)
cat << EOF
{
  "continue": true,
  "permission": "allow"
}
EOF

