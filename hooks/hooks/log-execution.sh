#!/bin/bash

# log-execution.sh - Logs shell command execution results
# Implements afterShellExecution hook

# Read JSON input from stdin
input=$(cat)

command=$(echo "$input" | jq -r '.command // empty')
output=$(echo "$input" | jq -r '.output // empty')
conversation_id=$(echo "$input" | jq -r '.conversation_id // empty')

# Create timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Log execution results
log_file="$HOME/.cursor/hooks/execution.log"
mkdir -p "$(dirname "$log_file")"

# Truncate output if too long (first 500 chars)
output_preview="${output:0:500}"
if [ ${#output} -gt 500 ]; then
  output_preview="${output_preview}... [truncated]"
fi

echo "[$timestamp] [EXEC] Conversation: $conversation_id | Command: $command | Output length: ${#output} chars" >> "$log_file"
echo "Output preview: $output_preview" >> "$log_file"
echo "---" >> "$log_file"

# No output needed for afterShellExecution
exit 0

