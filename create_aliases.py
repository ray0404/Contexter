#!/usr/bin/env bash

# 1. Detect the directory where this script is running (the repo folder)
# We use this to build absolute paths so the commands work from ANYWHERE.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📂 Detected Contexter repository at: $REPO_DIR"

# 2. Detect the shell configuration file
if [ -f "$HOME/.zshrc" ]; then
    CONFIG_FILE="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -f "$HOME/.bashrc" ]; then
    CONFIG_FILE="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    # Fallback for some lightweight environments
    CONFIG_FILE="$HOME/.profile"
    SHELL_NAME="profile"
fi

echo "⚙️  Adding aliases to: $CONFIG_FILE ($SHELL_NAME)"

# 3. Define the commands based on README.md/setup.py
# Format: "CommandName:ScriptFile.py"
COMMANDS=(
    "buildcontext:context_builder.py"
    "reconstructor:reconstructor.py"
    "sanitizecontext:sanitize_context.py"
    "updatecontext:update_context.py"
    "updater:updater.py"
    "smartupdate:smart_update.py"
    "buildcontexthtml:build_context_html.py"
    "reconstructorhtml:reconstructor_html.py"
    "updatecontexthtml:update_context_html.py"
    "updaterhtml:updater_html.py"
    "md2html:md2html.py"
    "html2md:html2md.py"
)

# 4. Append aliases to the config file
echo "" >> "$CONFIG_FILE"
echo "# --- Contexter Aliases (Added by create_aliases.sh) ---" >> "$CONFIG_FILE"

for entry in "${COMMANDS[@]}"; do
    KEY="${entry%%:*}"
    VAL="${entry##*:}"
    
    # We set PYTHONPATH so Python knows where to find 'contexter_utils.py' 
    # regardless of which folder you are currently in.
    ALIAS_CMD="alias $KEY='PYTHONPATH=\"$REPO_DIR\" python3 \"$REPO_DIR/$VAL\"'"
    
    # Check if alias already exists to avoid spamming the file
    if grep -q "alias $KEY=" "$CONFIG_FILE"; then
        echo "⚠️  Alias '$KEY' already exists in config. Skipping."
    else
        echo "$ALIAS_CMD" >> "$CONFIG_FILE"
        echo "✅ Added alias: $KEY -> $VAL"
    fi
done

echo "# ------------------------------------------------------" >> "$CONFIG_FILE"

echo ""
echo "🎉 Done! To start using the commands, reload your shell by running:"
echo "   source $CONFIG_FILE"
