# antigravity-statusline

A fast, lightweight, and customizable **Powerline-style statusline HUD** for **Google Antigravity CLI (`agy`)**.

Designed with the **Tokyo Night** palette and **Nerd Fonts**, it renders real-time session telemetry directly in your terminal footer.

---

## ✨ Features

### Subscription / Forfait view
```
 󰚩 Gemini 3.8 Flash (med)  󰍛 11.2%/1.0M  󰈚 117.3k tk  󰠠 $0.01  󰔛 5h: 70% (~3h57)  󰔚 Hebdo: 78%   ~/devel   main * 
```

### Pay-As-You-Go view (quotas disabled)
```
 󰚩 Gemini 3.8 Flash (med)  󰍛 11.2%/1.0M  󰈚 117.3k tk  󰠠 $0.01   ~/devel   main * 
```

* 󰚩 **Model & Thinking Effort**: Displays the current active model and its reasoning level (e.g. `low`, `med`, `high`).
* 󰍛 **Context Window Meter**: Context usage fraction and max size with automatic color transitions:
  * 🟣 **Purple** (< 40%)
  * 🟠 **Orange** (40% - 75%)
  * 🔴 **Red** (> 75%)
* 󰈚 **Token Metrics**: Total session tokens consumed (formatted with `tk` unit).
* 󰠠 **Real-time Cost Estimation**: Session cost calculated on-the-fly based on net inputs, prompt caching, and outputs.
* 󰔛 **5h Quota** *(optional)*: Remaining quota percentage with countdown until window reset.
* 󰔚 **Weekly Quota** *(optional)*: Remaining weekly quota fraction.
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

# Standard installation (Subscription / Forfait):
./install.sh --enable

# Pay-As-You-Go installation (hides 5h and weekly quotas):
./install.sh --enable --payg
```

### Installer Options

* `./install.sh`: Copies `statusline.py` to `~/.config/antigravity/statusline.py`.
* `./install.sh --link`: Symlinks `statusline.py` instead of copying (ideal for local development).
* `./install.sh --enable`: Updates your `~/.gemini/antigravity-cli/settings.json` automatically.
* `./install.sh --payg`: Disables 5h and weekly quota segments for Pay-As-You-Go setups.
* `./install.sh --test`: Runs a simulated render test to preview the display.

---

## 💳 Pay-As-You-Go Configuration

If your account is billed Pay-As-You-Go without subscription quota envelopes (5h / weekly), you can disable quota segments using any of the following methods:

### Method 1: CLI flag in `settings.json` (Recommended)
Add `--no-quotas` (or `--payg`) to the statusLine command in `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "statusLine": {
    "type": "",
    "command": "/Users/<your-user>/.config/antigravity/statusline.py --no-quotas",
    "enabled": true
  }
}
```

### Method 2: Config file `statusline.json`
Create or edit `~/.config/antigravity/statusline.json`:

```json
{
  "show_quotas": false
}
```

### Method 3: Environment variable
Set `STATUSLINE_HIDE_QUOTAS=1` in your shell environment (`.zshrc` / `.bashrc`).

---

## ⚙️ Manual Configuration

Place `statusline.py` in `~/.config/antigravity/` and make it executable:

```bash
mkdir -p ~/.config/antigravity
cp statusline.py ~/.config/antigravity/
chmod +x ~/.config/antigravity/statusline.py
```

Then edit `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "statusLine": {
    "type": "",
    "command": "/Users/<your-user>/.config/antigravity/statusline.py",
    "enabled": true
  }
}
```

---

## 🧪 Testing & Preview

Preview the statusline with mock payloads (including PAYG mode):

```bash
python3 test_statusline.py
```

---

## 🔗 CrewRig Integration

If you use [CrewRig](https://github.com/hcross/crewrig) usage capture, the CLI statusline is chained via `hooks/antigravity-statusline-shim.sh`. The shim delegates directly to `priorStatusLineCommand` defined in `~/.crewrig/usage/state/antigravity-statusline.json`, preserving this statusline without conflict.

---

## 📄 License

[MIT](LICENSE) © 2026 Hoani Cross
