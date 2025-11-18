#!/bin/bash

# observability.sh - Real-time Cursor agent observability
# Logs everything to a visible file and optionally prints to terminal

# Read JSON input from stdin
input=$(cat)

# Extract common fields
hook_event=$(echo "$input" | jq -r '.hook_event_name // "unknown"')
conversation_id=$(echo "$input" | jq -r '.conversation_id // "none"')
generation_id=$(echo "$input" | jq -r '.generation_id // "none"')
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Log file location (visible, easy to tail)
log_file="$HOME/.cursor/hooks/observability.log"
mkdir -p "$(dirname "$log_file")"

# Create log entry based on hook event
case "$hook_event" in
  "beforeShellExecution")
    command=$(echo "$input" | jq -r '.command // ""')
    cwd=$(echo "$input" | jq -r '.cwd // ""')
    echo "[$timestamp] 🔵 BEFORE SHELL | Conv: $conversation_id | CWD: $cwd | Command: $command" >> "$log_file"
    # Also print to stderr (visible in terminal)
    echo "[$timestamp] 🔵 BEFORE SHELL: $command" >&2
    ;;
  "afterShellExecution")
    command=$(echo "$input" | jq -r '.command // ""')
    output_length=$(echo "$input" | jq -r '.output | length // 0')
    echo "[$timestamp] 🟢 AFTER SHELL | Conv: $conversation_id | Command: $command | Output: ${output_length} chars" >> "$log_file"
    echo "[$timestamp] 🟢 AFTER SHELL: $command (${output_length} chars output)" >&2
    ;;
  "afterFileEdit")
    file_path=$(echo "$input" | jq -r '.file_path // ""')
    edits_count=$(echo "$input" | jq -r '.edits | length // 0')
    echo "[$timestamp] 📝 FILE EDIT | Conv: $conversation_id | File: $file_path | Edits: $edits_count" >> "$log_file"
    echo "[$timestamp] 📝 FILE EDIT: $file_path ($edits_count edits)" >&2
    ;;
  "beforeReadFile")
    file_path=$(echo "$input" | jq -r '.file_path // ""')
    echo "[$timestamp] 👁️  READ FILE | Conv: $conversation_id | File: $file_path" >> "$log_file"
    echo "[$timestamp] 👁️  READ FILE: $file_path" >&2
    ;;
  "beforeSubmitPrompt")
    prompt=$(echo "$input" | jq -r '.prompt // ""')
    prompt_preview="${prompt:0:100}..."
    attachments=$(echo "$input" | jq -r '.attachments | length // 0')
    echo "[$timestamp] 💬 PROMPT | Conv: $conversation_id | Attachments: $attachments | Prompt: $prompt_preview" >> "$log_file"
    echo "[$timestamp] 💬 PROMPT: $prompt_preview" >&2
    ;;
  "afterAgentResponse")
    text=$(echo "$input" | jq -r '.text // ""')
    text_length=${#text}
    code_blocks=$(echo "$text" | grep -o '```' | wc -l | tr -d ' ')
    echo "[$timestamp] 🤖 RESPONSE | Conv: $conversation_id | Length: $text_length chars | Code blocks: $code_blocks" >> "$log_file"
    echo "[$timestamp] 🤖 RESPONSE: $text_length chars, $code_blocks code blocks" >&2
    ;;
  "stop")
    status=$(echo "$input" | jq -r '.status // ""')
    loop_count=$(echo "$input" | jq -r '.loop_count // 0')
    echo "[$timestamp] 🛑 STOP | Conv: $conversation_id | Status: $status | Loops: $loop_count" >> "$log_file"
    echo "[$timestamp] 🛑 STOP: $status (after $loop_count loops)" >&2
    ;;
  *)
    echo "[$timestamp] ❓ UNKNOWN EVENT | Conv: $conversation_id | Event: $hook_event" >> "$log_file"
    echo "[$timestamp] ❓ UNKNOWN: $hook_event" >&2
    ;;
esac

# Always allow (this is observability only)
# For hooks that need responses, output JSON
if [[ "$hook_event" == "beforeShellExecution" ]] || [[ "$hook_event" == "beforeReadFile" ]]; then
  echo '{"permission": "allow"}'
fi

exit 0

