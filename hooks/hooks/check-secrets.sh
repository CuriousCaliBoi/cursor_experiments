#!/bin/bash

# check-secrets.sh - Checks for secrets in edited files
# Implements afterFileEdit hook

# Read JSON input from stdin
input=$(cat)

file_path=$(echo "$input" | jq -r '.file_path // empty')
edits=$(echo "$input" | jq -r '.edits // []')

# Read the file content (after edits)
if [ -f "$file_path" ]; then
  content=$(cat "$file_path")
  
  # Secret patterns to detect
  secret_patterns=(
    "ghp_[A-Za-z0-9]{36}"           # GitHub personal access token
    "ghs_[A-Za-z0-9]{36}"           # GitHub app token
    "gho_[A-Za-z0-9]{36}"           # GitHub OAuth token
    "sk-[A-Za-z0-9]{32,}"           # OpenAI API key
    "sk_live_[A-Za-z0-9]{24,}"      # Stripe live key
    "sk_test_[A-Za-z0-9]{24,}"      # Stripe test key
    "AKIA[0-9A-Z]{16}"               # AWS access key
    "AIza[0-9A-Za-z_-]{35}"         # Google API key
    "xox[baprs]-[0-9a-zA-Z-]{10,48}" # Slack token
  )
  
  # Check for secrets
  for pattern in "${secret_patterns[@]}"; do
    if echo "$content" | grep -qE "$pattern"; then
      log_file="$HOME/.cursor/hooks/secrets.log"
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: Potential secret detected in $file_path (pattern: $pattern)" >> "$log_file"
      
      # Note: We can't block here since this is afterFileEdit, but we log it
      # For blocking, use beforeReadFile hook instead
    fi
  done
fi

exit 0

