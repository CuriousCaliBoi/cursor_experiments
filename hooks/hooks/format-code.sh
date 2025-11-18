#!/bin/bash

# format-code.sh - Auto-formats code after file edits
# Implements afterFileEdit hook

# Read JSON input from stdin
input=$(cat)

file_path=$(echo "$input" | jq -r '.file_path // empty')
edits=$(echo "$input" | jq -r '.edits // []')

# Determine formatter based on file extension
formatter=""
case "$file_path" in
  *.py)
    formatter="black"
    ;;
  *.js|*.jsx|*.ts|*.tsx)
    formatter="prettier"
    ;;
  *.go)
    formatter="gofmt"
    ;;
  *.rs)
    formatter="rustfmt"
    ;;
esac

# If formatter is available, format the file
if [ -n "$formatter" ] && command -v "$formatter" &> /dev/null; then
  case "$formatter" in
    black)
      black "$file_path" 2>/dev/null || true
      ;;
    prettier)
      prettier --write "$file_path" 2>/dev/null || true
      ;;
    gofmt)
      gofmt -w "$file_path" 2>/dev/null || true
      ;;
    rustfmt)
      rustfmt "$file_path" 2>/dev/null || true
      ;;
  esac
  
  # Log formatting action
  log_file="$HOME/.cursor/hooks/format.log"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Formatted $file_path using $formatter" >> "$log_file"
fi

# No output needed for afterFileEdit
exit 0

