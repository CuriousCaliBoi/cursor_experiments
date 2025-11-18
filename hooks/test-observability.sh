#!/bin/bash

# test-observability.sh - Test the observability hook with sample events

echo "🧪 Testing Cursor Observability Hook"
echo "====================================="
echo ""

HOOK_SCRIPT="$HOME/.cursor/hooks/observability.sh"

if [ ! -f "$HOOK_SCRIPT" ]; then
    echo "❌ Hook not found at $HOOK_SCRIPT"
    echo "   Run: ./QUICKSTART.sh first"
    exit 1
fi

echo "Testing different hook events..."
echo ""

# Test beforeShellExecution
echo "1. Testing beforeShellExecution..."
echo '{"hook_event_name": "beforeShellExecution", "conversation_id": "test-123", "command": "ls -la", "cwd": "/tmp"}' | "$HOOK_SCRIPT"
echo ""

# Test afterFileEdit
echo "2. Testing afterFileEdit..."
echo '{"hook_event_name": "afterFileEdit", "conversation_id": "test-123", "file_path": "/tmp/test.py", "edits": [{"old": "x", "new": "y"}, {"old": "a", "new": "b"}]}' | "$HOOK_SCRIPT"
echo ""

# Test beforeSubmitPrompt
echo "3. Testing beforeSubmitPrompt..."
echo '{"hook_event_name": "beforeSubmitPrompt", "conversation_id": "test-123", "prompt": "Create a Python function to calculate fibonacci", "attachments": []}' | "$HOOK_SCRIPT"
echo ""

# Test afterAgentResponse
echo "4. Testing afterAgentResponse..."
echo '{"hook_event_name": "afterAgentResponse", "conversation_id": "test-123", "text": "Here is the code:\n```python\ndef fib(n):\n    return n\n```"}' | "$HOOK_SCRIPT"
echo ""

echo "✅ Test complete!"
echo ""
echo "📋 Check the log file:"
echo "   tail -f ~/.cursor/hooks/observability.log"
echo ""
echo "💡 To watch live:"
echo "   ./watch.sh"

