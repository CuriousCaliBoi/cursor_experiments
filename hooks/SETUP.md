# Cursor Hooks Setup Guide

Quick setup guide for using Cursor hooks in this project.

## Prerequisites

- Cursor IDE installed
- `jq` command-line JSON processor (for parsing JSON in hooks)
  - macOS: `brew install jq`
  - Linux: `sudo apt-get install jq` or `sudo yum install jq`
  - Windows: Download from https://stedolan.github.io/jq/download/

## Installation Steps

### 1. Copy Configuration Files

```bash
# Navigate to the hooks directory
cd /Users/princezuk0/projects/cursor_experiments/hooks

# Copy hooks.json to Cursor config directory
cp hooks.json ~/.cursor/hooks.json

# Copy hooks scripts directory
cp -r hooks ~/.cursor/hooks
```

### 2. Make Scripts Executable

```bash
chmod +x ~/.cursor/hooks/*.sh
```

### 3. Verify Installation

Check that files are in place:

```bash
ls -la ~/.cursor/hooks.json
ls -la ~/.cursor/hooks/
```

### 4. Restart Cursor

**Important**: Restart Cursor completely for hooks to take effect.

### 5. Verify Hooks Are Active

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Navigate to the "Hooks" tab
3. You should see your hooks listed and their execution status

## Testing Hooks

### Test Security Hook

Try running a dangerous command in Cursor's chat:
```
Run: rm -rf /
```

The `security-check.sh` hook should block it.

### Test Format Hook

Edit a Python file and save it. The `format-code.sh` hook should automatically format it if `black` is installed.

### Test Audit Hook

Run any shell command through Cursor. Check `~/.cursor/hooks/audit.log` to see if it was logged.

## Troubleshooting

### Hooks Not Running

1. **Check file permissions**: Ensure scripts are executable
   ```bash
   ls -la ~/.cursor/hooks/*.sh
   ```

2. **Check paths**: Ensure paths in `hooks.json` are correct
   - Relative paths should be relative to `hooks.json` location
   - Or use absolute paths

3. **Check Cursor logs**: 
   - Cursor Settings → Hooks tab shows hook execution status
   - Check the Hooks output channel for errors

4. **Restart Cursor**: Hooks are loaded on startup

### Script Errors

Check the Hooks output channel in Cursor for error messages. Common issues:

- **jq not found**: Install jq (see Prerequisites)
- **Permission denied**: Make scripts executable with `chmod +x`
- **Path issues**: Use absolute paths or ensure relative paths are correct

### Log Files Not Created

Log files are created in `~/.cursor/hooks/`. Ensure the directory exists:

```bash
mkdir -p ~/.cursor/hooks
```

## Uninstalling

To remove hooks:

```bash
rm ~/.cursor/hooks.json
rm -rf ~/.cursor/hooks
```

Then restart Cursor.

## Next Steps

- Customize hooks for your workflow
- Add new hooks for specific use cases
- Review log files to understand agent behavior
- Share hooks with your team (see Cursor docs for team distribution)

