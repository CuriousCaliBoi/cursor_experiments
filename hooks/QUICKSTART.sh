#!/bin/bash
# Quickstart: Get Cursor hooks running in 30 seconds

set -e

echo "🚀 Cursor Hooks Quickstart"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is required. Install it:"
    echo "   macOS: brew install jq"
    echo "   Linux: sudo apt-get install jq"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy hooks.json
echo "📋 Copying hooks.json..."
cp "$SCRIPT_DIR/hooks.json" ~/.cursor/hooks.json

# Copy hooks directory
echo "📁 Copying hooks scripts..."
mkdir -p ~/.cursor/hooks
cp -r "$SCRIPT_DIR/hooks"/* ~/.cursor/hooks/

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x ~/.cursor/hooks/*.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart Cursor"
echo "   2. Check Cursor Settings → Hooks tab to verify"
echo "   3. Try asking Cursor to run 'rm -rf /' (it should be blocked)"
echo ""
echo "📚 Read TUTORIAL.md for a 5-minute guide"

