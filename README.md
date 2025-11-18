# Cursor Hooks Experiments

Experiments using [Cursor's hooks feature](https://cursor.com/docs/agent/hooks) to observe, control, and extend the agent loop.

## 🚀 Quick Start

**New to hooks?** Start here:
1. **[hooks/TUTORIAL.md](hooks/TUTORIAL.md)** - 5-minute mastery guide (read this first!)
2. **`./hooks/QUICKSTART.sh`** - One-command setup
3. **[hooks/SETUP.md](hooks/SETUP.md)** - Detailed installation guide

## What are Cursor Hooks?

Cursor hooks are shell scripts that integrate with Cursor's agent loop. They run before or after defined stages and can:
- **Observe** agent behavior (logging, analytics)
- **Control** agent actions (block dangerous commands, gate operations)
- **Extend** functionality (format code, enhance prompts, add context)

Hooks communicate with Cursor via JSON over stdio, allowing you to customize the agent's behavior.

## Setup

### 1. Copy hooks.json to your Cursor config directory

```bash
# Copy the hooks.json file to your Cursor home directory
cp hooks/hooks.json ~/.cursor/hooks.json

# Copy the hooks scripts directory
cp -r hooks/hooks ~/.cursor/hooks
```

### 2. Make scripts executable

```bash
chmod +x ~/.cursor/hooks/*.sh
```

### 3. Restart Cursor

Restart Cursor for the hooks to take effect. You can verify hooks are active in Cursor Settings → Hooks tab.

## Available Hooks

### 🔒 Security Hooks

#### `security-check.sh` (beforeShellExecution)
Blocks dangerous shell commands like `rm -rf /`, `format C:`, etc. Prevents accidental destructive operations.

#### `redact-secrets.sh` (beforeReadFile)
Prevents the agent from reading files containing API keys, tokens, or other secrets. Blocks access to sensitive files.

#### `check-secrets.sh` (afterFileEdit)
Scans edited files for potential secrets and logs warnings. Helps prevent accidental secret commits.

### 📝 Code Quality Hooks

#### `format-code.sh` (afterFileEdit)
Automatically formats code after edits using appropriate formatters:
- Python → `black`
- JavaScript/TypeScript → `prettier`
- Go → `gofmt`
- Rust → `rustfmt`

### 📊 Analytics & Logging Hooks

#### `audit-shell.sh` (beforeShellExecution)
Logs all shell commands executed by the agent with timestamps, conversation IDs, and working directories.

#### `log-execution.sh` (afterShellExecution)
Logs command execution results and output for debugging and analysis.

#### `enhance-prompt.sh` (beforeSubmitPrompt)
Logs all prompts submitted to the agent for analytics and can be extended to enhance prompts with context.

#### `analyze-response.sh` (afterAgentResponse)
Analyzes agent responses, counting code blocks, links, and response length.

#### `finalize-session.sh` (stop)
Logs session completion and can optionally trigger follow-up actions.

## Hook Events

The hooks are configured to run at these stages:

- **beforeShellExecution** - Before any shell command runs
- **afterShellExecution** - After shell commands complete
- **afterFileEdit** - After files are edited
- **beforeReadFile** - Before files are read
- **beforeSubmitPrompt** - Before prompts are submitted
- **afterAgentResponse** - After agent responses
- **stop** - When agent loop ends

## Log Files

Hooks create log files in `~/.cursor/hooks/`:

- `audit.log` - Shell command audit trail
- `execution.log` - Command execution results
- `format.log` - Code formatting actions
- `secrets.log` - Secret detection warnings
- `prompts.log` - Prompt analytics
- `response-analysis.log` - Response analysis
- `sessions.log` - Session tracking

## Customization

### Adding New Hooks

1. Create a new shell script in `hooks/hooks/` directory
2. Add it to `hooks/hooks.json` with the appropriate event
3. Ensure the script reads JSON from stdin and outputs JSON to stdout
4. Make it executable: `chmod +x hooks/hooks/your-hook.sh`

### Modifying Existing Hooks

Edit the shell scripts directly. They follow this pattern:

```bash
#!/bin/bash
# Read JSON input
input=$(cat)
# Parse fields
field=$(echo "$input" | jq -r '.field // empty')
# Do something
# Output JSON response (if needed)
cat << EOF
{
  "permission": "allow"
}
EOF
```

## Examples

### Block Git Commands

Add to `security-check.sh`:

```bash
if [[ "$command" == git* ]]; then
  cat << EOF
{
  "permission": "deny",
  "user_message": "Git commands blocked. Use GitHub CLI instead."
}
EOF
fi
```

### Auto-format on Save

The `format-code.sh` hook already does this, but you can customize formatters or add linting:

```bash
# Add linting after formatting
if [ -f "$file_path" ] && [[ "$file_path" == *.py ]]; then
  pylint "$file_path" 2>/dev/null || true
fi
```

### Enhanced Prompt Context

Modify `enhance-prompt.sh` to add context:

```bash
# Add git context to prompts
git_status=$(git status --short 2>/dev/null || echo "")
enhanced_prompt="$prompt\n\nGit Status:\n$git_status"
```

## Project Structure

```
cursor_experiments/
├── hooks/
│   ├── hooks/              # Shell script hooks
│   │   ├── analyze-response.sh
│   │   ├── audit-shell.sh
│   │   ├── check-secrets.sh
│   │   ├── enhance-prompt.sh
│   │   ├── finalize-session.sh
│   │   ├── format-code.sh
│   │   ├── log-execution.sh
│   │   ├── redact-secrets.sh
│   │   └── security-check.sh
│   ├── hooks.json          # Hook configuration
│   ├── QUICKSTART.sh       # Quick setup script
│   ├── README.md           # Detailed hooks documentation
│   ├── SETUP.md            # Installation guide
│   └── TUTORIAL.md         # 5-minute tutorial
└── README.md               # This file
```

## Reference

- [Cursor Hooks Documentation](https://cursor.com/docs/agent/hooks)
- [Hook Events Reference](https://cursor.com/docs/agent/hooks#hook-events)
- [Configuration Guide](https://cursor.com/docs/agent/hooks#configuration)

## Philosophy

These hooks demonstrate:
- **Security**: Protecting against dangerous operations
- **Quality**: Ensuring code quality through formatting and linting
- **Observability**: Logging and analytics for understanding agent behavior
- **Extensibility**: Easy to customize and extend for your needs
