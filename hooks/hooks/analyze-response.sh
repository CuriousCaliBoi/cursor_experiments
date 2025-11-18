#!/bin/bash

# analyze-response.sh - Analyzes agent responses
# Implements afterAgentResponse hook

# Read JSON input from stdin
input=$(cat)

text=$(echo "$input" | jq -r '.text // empty')
conversation_id=$(echo "$input" | jq -r '.conversation_id // empty')

# Simple analysis: count code blocks, links, etc.
code_blocks=$(echo "$text" | grep -c '```' || echo "0")
link_count=$(echo "$text" | grep -oE 'https?://[^[:space:]]+' | wc -l | tr -d ' ')

# Log analysis
log_file="$HOME/.cursor/hooks/response-analysis.log"
mkdir -p "$(dirname "$log_file")"

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$timestamp] [RESPONSE] Conversation: $conversation_id | Length: ${#text} chars | Code blocks: $code_blocks | Links: $link_count" >> "$log_file"

# No output needed for afterAgentResponse
exit 0

