#!/bin/bash

# security-check.sh - Security checks for shell commands
# Blocks dangerous commands like rm -rf, format C:, etc.

# Read JSON input from stdin
input=$(cat)
command=$(echo "$input" | jq -r '.command // empty')

# Dangerous patterns to block
dangerous_patterns=(
  "rm -rf /"
  "rm -rf ~"
  "format C:"
  "mkfs"
  "dd if="
  ":(){ :|:& };:"
  "chmod -R 777 /"
)

# Check for dangerous commands
for pattern in "${dangerous_patterns[@]}"; do
  if [[ "$command" == *"$pattern"* ]]; then
    cat << EOF
{
  "continue": true,
  "permission": "deny",
  "user_message": "Dangerous command blocked: $command",
  "agent_message": "The command '$command' matches a dangerous pattern and has been blocked for security reasons. Please use safer alternatives."
}
EOF
    exit 0
  fi
done

# Allow safe commands
cat << EOF
{
  "continue": true,
  "permission": "allow"
}
EOF

