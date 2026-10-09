# antigravity-statusline

A fast, lightweight, and customizable **Powerline-style statusline HUD** for **Google Antigravity CLI (`agy`)**.

Designed with the **Tokyo Night** palette and **Nerd Fonts**, it renders real-time session telemetry directly in your terminal footer.

---

## ✨ Features

```
 󰚩 Gemini 3.8 Flash (med)  󰍛 11.2%/1.0M  󰈚 117.3k tk  󰠠 $0.01  󰔛 5h: 70% (~3h57)  󰔚 Hebdo: 78%   ~/devel   main * 
```

* 󰚩 **Model & Thinking Effort**: Displays the current active model and its reasoning level (e.g. `low`, `med`, `high`).
* 󰍛 **Context Window Meter**: Context usage fraction and max size with automatic color transitions:
  * 🟣 **Purple** (< 40%)
  * 🟠 **Orange** (40% - 75%)
  * 🔴 **Red** (> 75%)
* 󰈚 **Token Metrics**: Total session tokens consumed (formatted with `tk` unit).
* 󰠠 **Real-time Cost Estimation**: Session cost calculated on-the-fly based on net inputs, prompt caching, and outputs.
* 󰔛 **5h Quota**: Remaining quota percentage with countdown until window reset.
* 󰔚 **Weekly Quota**: Remaining weekly quota fraction.
*  **Working Directory**: Shortened path representation.
*  **Git Integration**: Active branch name and dirty working tree indicator (`*`).

---

## 📋 Prerequisites

* **Python 3.8+** (standard library only, no external pip dependencies)
* **Git** (for branch and dirty status detection)
* **A Nerd Font** (e.g. *FiraCode Nerd Font*, *JetBrainsMono NF*, *MesloLGS NF*) configured in your terminal for Powerline glyphs (``, `󰚩`, `󰍛`, `󰈚`, `󰠠`, `󰔛`, `󰔚`, ``, ``).

---

## 🚀 Quick Install

Clone this repository and run the install script:

```bash
git clone https://github.com/hcross/antigravity-statusline.git
cd antigravity-statusline

# Install and automatically enable in ~/.gemini/antigravity-cli/settings.json:
./install.sh --enable
```

### Options

* `./install.sh`: Copies `statusline.py` to `~/.config/antigravity/statusline.py`.
* `./install.sh --link`: Symlinks `statusline.py` instead of copying (ideal for local development).
* `./install.sh --enable`: Updates your `~/.gemini/antigravity-cli/settings.json` automatically.
* `./install.sh --test`: Runs a simulated render test to preview the display.

---

## ⚙️ Manual Configuration

If you prefer to configure manually, place `statusline.py` in `~/.config/antigravity/` and make it executable:

```bash
mkdir -p ~/.config/antigravity
cp statusline.py ~/.config/antigravity/
chmod +x ~/.config/antigravity/statusline.py
```

Then edit `~/.gemini/antigravity-cli/settings.json` to register the statusLine command:

```json
{
  "statusLine": {
    "type": "",
    "command": "/Users/<your-user>/.config/antigravity/statusline.py",
    "enabled": true
  }
}
```

> **Note**: You can also use `python3 ~/.config/antigravity/statusline.py` or the absolute path to your Python interpreter.

---

## 🧪 Testing & Preview

To preview the statusline with mock payloads:

```bash
python3 test_statusline.py
```

Or test via stdin directly:

```bash
echo '{
  "cwd": "'"$PWD"'",
  "model": {"display_name": "Gemini 3.8 Flash (Medium)", "effort": "medium"},
  "context_window": {
    "total_input_tokens": 125000,
    "total_output_tokens": 15000,
    "context_window_size": 1048576,
    "used_percentage": 13.3,
    "current_usage": {"cache_read_input_tokens": 110000}
  },
  "quota": {
    "gemini-5h": {"remaining_fraction": 0.82, "reset_in_seconds": 12400},
    "gemini-weekly": {"remaining_fraction": 0.91, "reset_in_seconds": 250000}
  }
}' | python3 statusline.py
```

---

## 🔗 CrewRig Integration

If you use [CrewRig](https://github.com/hcross/crewrig) usage capture, the CLI statusline is chained via `hooks/antigravity-statusline-shim.sh`. The shim delegates directly to `priorStatusLineCommand` defined in `~/.crewrig/usage/state/antigravity-statusline.json`, preserving this statusline without conflict.

---

## 📄 License

[MIT](LICENSE) © 2026 Hoani Cross
