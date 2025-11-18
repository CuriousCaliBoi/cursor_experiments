#!/bin/bash

# enhance-prompt.sh - Enhances prompts before submission
# Implements beforeSubmitPrompt hook
# This is a pass-through hook that logs prompts but doesn't modify them

# Read JSON input from stdin
input=$(cat)

prompt=$(echo "$input" | jq -r '.prompt // empty')
attachments=$(echo "$input" | jq -r '.attachments // []')
conversation_id=$(echo "$input" | jq -r '.conversation_id // empty')

# Log the prompt for analytics
log_file="$HOME/.cursor/hooks/prompts.log"
mkdir -p "$(dirname "$log_file")"

timestamp=$(date '+%Y-%m-%d %H:%M:%S')
attachment_count=$(echo "$attachments" | jq 'length')

echo "[$timestamp] [PROMPT] Conversation: $conversation_id | Attachments: $attachment_count | Prompt length: ${#prompt} chars" >> "$log_file"
echo "Prompt preview: ${prompt:0:200}..." >> "$log_file"
echo "---" >> "$log_file"

# Allow the prompt to continue (no modification)
# Note: This hook could be extended to modify prompts, add context, etc.
cat << EOF
{
  "continue": true
}
EOF

