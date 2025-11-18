# Cursor Hooks: 5-Minute Mastery

**Goal**: Control Cursor's AI agent with custom scripts. **Time**: 5 minutes.

## The 30-Second Setup

```bash
# 1. Create config
mkdir -p ~/.cursor/hooks
cp hooks.json ~/.cursor/hooks.json
cp -r hooks ~/.cursor/hooks
chmod +x ~/.cursor/hooks/*.sh

# 2. Restart Cursor
# Done. Hooks are now active.
```

## How Hooks Work (30 seconds)

Cursor sends JSON to your script via stdin. Your script outputs JSON to stdout.

```bash
# Input (from Cursor)
{"command": "rm -rf /", "cwd": "/home/user"}

# Your script processes it
# Output (to Cursor)
{"permission": "deny", "user_message": "Blocked!"}
```

## The 3 Most Powerful Hooks

### 1. Block Dangerous Commands

**Hook**: `beforeShellExecution`  
**Impact**: Prevents disasters

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.command')

if [[ "$cmd" == *"rm -rf"* ]] || [[ "$cmd" == *"format"* ]]; then
  echo '{"permission": "deny", "user_message": "Dangerous command blocked"}'
else
  echo '{"permission": "allow"}'
fi
```

**Try it**: Ask Cursor to run `rm -rf /`. It gets blocked.

### 2. Auto-Format Code

**Hook**: `afterFileEdit`  
**Impact**: Code always formatted

```bash
#!/bin/bash
input=$(cat)
file=$(echo "$input" | jq -r '.file_path')

[[ "$file" == *.py ]] && black "$file" 2>/dev/null
[[ "$file" == *.js ]] && prettier --write "$file" 2>/dev/null

exit 0
```

**Try it**: Edit a Python file. It auto-formats on save.

### 3. Secret Detection

**Hook**: `beforeReadFile`  
**Impact**: Prevents secret leaks

```bash
#!/bin/bash
input=$(cat)
content=$(echo "$input" | jq -r '.content')

if echo "$content" | grep -qE 'ghp_|sk-[a-zA-Z0-9]{32}'; then
  echo '{"permission": "deny"}'
else
  echo '{"permission": "allow"}'
fi
```

**Try it**: Agent can't read files with GitHub tokens.

## Hook Events Cheat Sheet

| Event | When | Use For |
|-------|------|---------|
| `beforeShellExecution` | Before command runs | Block/modify commands |
| `afterShellExecution` | After command runs | Log results |
| `afterFileEdit` | After file saved | Format, lint, scan |
| `beforeReadFile` | Before file read | Access control |
| `beforeSubmitPrompt` | Before prompt sent | Enhance/modify prompts |
| `afterAgentResponse` | After response | Analyze, log |
| `stop` | Loop ends | Cleanup, follow-up |

## The Minimal Hook Template

```bash
#!/bin/bash
# 1. Read input
input=$(cat)

# 2. Parse what you need
field=$(echo "$input" | jq -r '.field // empty')

# 3. Do your thing
# ... your logic here ...

# 4. Output response (if needed)
echo '{"permission": "allow"}'
```

## Real-World Example: Smart Git Blocking

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.command')

# Block destructive git commands
if [[ "$cmd" == "git push --force"* ]] || [[ "$cmd" == "git reset --hard"* ]]; then
  cat << EOF
{
  "permission": "deny",
  "user_message": "Destructive git command blocked",
  "agent_message": "Use safer alternatives like 'git push' or 'git reset --soft'"
}
EOF
elif [[ "$cmd" == git* ]]; then
  # Ask permission for other git commands
  echo '{"permission": "ask", "user_message": "Git command requires approval"}'
else
  echo '{"permission": "allow"}'
fi
```

## Debugging

**Check if hooks run**: Cursor Settings → Hooks tab

**See errors**: Hooks output channel in Cursor

**Test manually**:
```bash
echo '{"command": "ls"}' | ~/.cursor/hooks/your-hook.sh
```

## The One-Liner Hook

Want to log all commands? One line:

```bash
#!/bin/bash
echo "[$(date)] $(cat | jq -r '.command')" >> ~/.cursor/hooks/commands.log
echo '{"permission": "allow"}'
```

## Pro Tips

1. **Always allow by default** - Only block when necessary
2. **Use `jq`** - It's installed, use it for JSON parsing
3. **Log everything** - Debugging hooks is hard without logs
4. **Test incrementally** - Start with logging, add blocking later
5. **Relative paths** - Use `./hooks/script.sh` in `hooks.json`

## Common Patterns

**Pattern: Conditional Block**
```bash
if dangerous; then
  echo '{"permission": "deny"}'
else
  echo '{"permission": "allow"}'
fi
```

**Pattern: Log and Allow**
```bash
echo "$(date): $(cat | jq -r '.command')" >> log.txt
echo '{"permission": "allow"}'
```

**Pattern: Modify Prompt**
```bash
prompt=$(cat | jq -r '.prompt')
enhanced="$prompt\n\nContext: $(git status)"
echo "{\"continue\": true, \"prompt\": \"$enhanced\"}"
```

## You're Done

You now know:
- ✅ How hooks work (JSON in/out)
- ✅ The 3 most powerful hooks
- ✅ How to write your own
- ✅ How to debug them

**Next**: Customize the existing hooks or create new ones for your workflow.

---

**Reference**: [Full Cursor Hooks Docs](https://cursor.com/docs/agent/hooks)

