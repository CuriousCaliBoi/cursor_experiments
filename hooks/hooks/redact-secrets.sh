#!/bin/bash

# redact-secrets.sh - Blocks reading files with secrets
# Implements beforeReadFile hook

# Read JSON input from stdin
input=$(cat)

file_path=$(echo "$input" | jq -r '.file_path // empty')
content=$(echo "$input" | jq -r '.content // empty')

# Secret patterns to detect
secret_patterns=(
  "ghp_[A-Za-z0-9]{36}"           # GitHub personal access token
  "ghs_[A-Za-z0-9]{36}"           # GitHub app token
  "sk-[A-Za-z0-9]{32,}"           # OpenAI API key
  "sk_live_[A-Za-z0-9]{24,}"      # Stripe live key
  "AKIA[0-9A-Z]{16}"               # AWS access key
  "AIza[0-9A-Za-z_-]{35}"         # Google API key
)

# Check for secrets in content
for pattern in "${secret_patterns[@]}"; do
  if echo "$content" | grep -qE "$pattern"; then
    cat << EOF
{
  "permission": "deny"
}
EOF
    exit 0
  fi
done

# Allow reading if no secrets detected
cat << EOF
{
  "permission": "allow"
}
EOF

