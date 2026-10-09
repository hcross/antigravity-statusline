#!/usr/bin/env bash
# install.sh — Installer for antigravity-statusline
#
# Usage:
#   ./install.sh                Copy statusline.py to ~/.config/antigravity/
#   ./install.sh --link         Symlink statusline.py to ~/.config/antigravity/
#   ./install.sh --enable       Configure statusLine in ~/.gemini/antigravity-cli/settings.json
#   ./install.sh --payg         Disable quotas for pay-as-you-go setups (can be combined with --enable)
#   ./install.sh --test         Run a test render to preview the statusline
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
TARGET_DIR="${HOME}/.config/antigravity"
TARGET_FILE="${TARGET_DIR}/statusline.py"
CONFIG_FILE="${TARGET_DIR}/statusline.json"
SETTINGS_FILE="${HOME}/.gemini/antigravity-cli/settings.json"

info() { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
success() { printf '\033[1;32m[OK]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

USE_SYMLINK=false
UPDATE_SETTINGS=false
PAYG_MODE=false
HIDE_COST=false
RUN_TEST=false

for arg in "$@"; do
  case "$arg" in
    --link|-l)
      USE_SYMLINK=true
      ;;
    --enable|-e)
      UPDATE_SETTINGS=true
      ;;
    --payg|--pay-as-you-go|--no-quotas)
      PAYG_MODE=true
      ;;
    --no-cost|--hide-cost|--no-price|--hide-price)
      HIDE_COST=true
      ;;
    --test|-t)
      RUN_TEST=true
      ;;
    --help|-h)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  --link, -l      Symlink instead of copying statusline.py"
      echo "  --enable, -e    Update ~/.gemini/antigravity-cli/settings.json automatically"
      echo "  --payg          Disable quota segments for Pay-As-You-Go accounts"
      echo "  --no-cost       Disable estimated price / cost display"
      echo "  --test, -t      Run preview render"
      echo "  --help, -h      Show this help message"
      exit 0
      ;;
    *)
      fail "Unknown option: $arg"
      ;;
  esac
done

# Check Python 3
command -v python3 >/dev/null 2>&1 || fail "python3 is required but not found in PATH."

mkdir -p "$TARGET_DIR"
chmod +x "${SCRIPT_DIR}/statusline.py"

if [ "$USE_SYMLINK" = true ]; then
  ln -sf "${SCRIPT_DIR}/statusline.py" "$TARGET_FILE"
  success "Symlinked ${SCRIPT_DIR}/statusline.py -> $TARGET_FILE"
else
  cp "${SCRIPT_DIR}/statusline.py" "$TARGET_FILE"
  chmod +x "$TARGET_FILE"
  success "Installed statusline.py to $TARGET_FILE"
fi

if [ "$PAYG_MODE" = true ] || [ "$HIDE_COST" = true ]; then
  python3 - <<EOF
import json, os
conf_path = os.path.expanduser("${CONFIG_FILE}")
conf = {}
if os.path.isfile(conf_path):
    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            conf = json.load(f)
    except Exception:
        pass
if "${PAYG_MODE}" == "true":
    conf["show_quotas"] = False
if "${HIDE_COST}" == "true":
    conf["show_cost"] = False
with open(conf_path, "w", encoding="utf-8") as f:
    json.dump(conf, f, indent=2)
    f.write("\n")
EOF
  if [ "$PAYG_MODE" = true ]; then
    success "Configured Pay-As-You-Go mode (quotas disabled in $CONFIG_FILE)"
  fi
  if [ "$HIDE_COST" = true ]; then
    success "Configured price display disabled in $CONFIG_FILE"
  fi
fi

CMD_ARGS=""
if [ "$PAYG_MODE" = true ]; then
  CMD_ARGS="${CMD_ARGS} --no-quotas"
fi
if [ "$HIDE_COST" = true ]; then
  CMD_ARGS="${CMD_ARGS} --no-cost"
fi
CMD_STR="${TARGET_FILE}${CMD_ARGS}"

if [ "$UPDATE_SETTINGS" = true ]; then
  if [ -f "$SETTINGS_FILE" ]; then
    python3 - <<EOF
import json, os

settings_path = os.path.expanduser("${SETTINGS_FILE}")
try:
    with open(settings_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}

data["statusLine"] = {
    "type": "",
    "command": "${CMD_STR}",
    "enabled": True
}

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
EOF
    success "Configured statusLine in $SETTINGS_FILE"
  else
    warn "$SETTINGS_FILE not found. Please configure it manually when Antigravity CLI is installed."
  fi
else
  info "To enable in Antigravity CLI, ensure ~/.gemini/antigravity-cli/settings.json includes:"
  echo '  "statusLine": {'
  echo '    "type": "",'
  echo "    \"command\": \"${CMD_STR}\","
  echo '    "enabled": true'
  echo '  }'
fi

if [ "$RUN_TEST" = true ]; then
  echo ""
  python3 "${SCRIPT_DIR}/test_statusline.py"
fi

echo ""
success "Setup complete! Make sure your terminal uses a Nerd Font for full Powerline icon rendering."
