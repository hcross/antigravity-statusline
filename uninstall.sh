#!/usr/bin/env bash
# uninstall.sh — Uninstaller for antigravity-statusline
#
# Removes statusline files from ~/.config/antigravity/ and cleans up
# the statusLine entry in ~/.gemini/antigravity-cli/settings.json.
set -euo pipefail

TARGET_DIR="${HOME}/.config/antigravity"
TARGET_FILE="${TARGET_DIR}/statusline.py"
CONFIG_FILE="${TARGET_DIR}/statusline.json"
SETTINGS_FILE="${HOME}/.gemini/antigravity-cli/settings.json"

info() { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
success() { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }

info "Uninstalling antigravity-statusline..."

# 1. Remove statusline.py
if [ -L "$TARGET_FILE" ] || [ -f "$TARGET_FILE" ]; then
  rm -f "$TARGET_FILE"
  success "Removed $TARGET_FILE"
else
  info "$TARGET_FILE was not found."
fi

# 2. Remove statusline.json
if [ -f "$CONFIG_FILE" ]; then
  rm -f "$CONFIG_FILE"
  success "Removed $CONFIG_FILE"
fi

# 3. Clean up directory if empty
if [ -d "$TARGET_DIR" ]; then
  if [ -z "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR" 2>/dev/null || true
    success "Removed empty directory $TARGET_DIR"
  fi
fi

# 4. Clean up Antigravity CLI settings.json if configured
if [ -f "$SETTINGS_FILE" ] && command -v python3 >/dev/null 2>&1; then
  python3 - <<EOF
import json, os

settings_path = os.path.expanduser("${SETTINGS_FILE}")
try:
    with open(settings_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}

if "statusLine" in data:
    cmd = data["statusLine"].get("command", "")
    if "statusline.py" in cmd:
        del data["statusLine"]
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print("SETTINGS_CLEANED")
    else:
        print("SETTINGS_SKIPPED")
EOF
fi

echo ""
success "antigravity-statusline has been completely uninstalled."
