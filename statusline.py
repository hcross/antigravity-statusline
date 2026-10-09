#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import re
import argparse

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def format_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}k" if n < 10_000 else f"{n/1_000:.0f}k"
    return str(n)

def format_duration(seconds):
    if seconds <= 0:
        return "0m"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h{minutes:02d}"
    return f"{minutes}m"

def estimate_cost(model_name, total_in, total_out, cache_in=0):
    name = (model_name or "").lower()
    if "pro" in name:
        in_rate = 1.25 / 1_000_000
        cache_rate = 0.3125 / 1_000_000
        out_rate = 5.00 / 1_000_000
    elif "sonnet" in name:
        in_rate = 3.00 / 1_000_000
        cache_rate = 0.30 / 1_000_000
        out_rate = 15.00 / 1_000_000
    elif "haiku" in name:
        in_rate = 0.80 / 1_000_000
        cache_rate = 0.08 / 1_000_000
        out_rate = 4.00 / 1_000_000
    else:  # Flash / default
        in_rate = 0.075 / 1_000_000
        cache_rate = 0.01875 / 1_000_000
        out_rate = 0.30 / 1_000_000

    net_in = max(0, total_in - cache_in)
    cost = (net_in * in_rate) + (cache_in * cache_rate) + (total_out * out_rate)
    return cost

def format_cost(cost):
    if cost < 0.005:
        return f"${cost:.3f}"
    return f"${cost:.2f}"

def get_git_info(cwd):
    if not cwd or not os.path.isdir(cwd):
        return None
    try:
        res = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.2
        )
        if res.returncode != 0:
            return None
        branch = res.stdout.strip()
        if not branch:
            return None
        if branch == "HEAD":
            res_short = subprocess.run(
                ["git", "-C", cwd, "rev-parse", "--short", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=0.2
            )
            branch = f":{res_short.stdout.strip()}"

        res_diff = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.2
        )
        is_dirty = bool(res_diff.stdout.strip())
        return branch, is_dirty
    except Exception:
        return None

def shorten_path(p):
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    parts = p.split(os.sep)
    if len(parts) > 3:
        return os.path.join(parts[0], "…", parts[-1])
    return p

def load_config():
    config = {
        "show_quotas": True,
        "show_cost": True,
        "show_git": True,
        "show_dir": True,
    }

    # 1. Config file (statusline.json in ~/.config/antigravity or script directory)
    candidates = [
        os.path.expanduser("~/.config/antigravity/statusline.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "statusline.json")
    ]
    for conf_path in candidates:
        if os.path.isfile(conf_path):
            try:
                with open(conf_path, "r", encoding="utf-8") as f:
                    user_conf = json.load(f)
                    if isinstance(user_conf, dict):
                        config.update(user_conf)
                break
            except Exception:
                pass

    # 2. Environment variables
    if os.environ.get("STATUSLINE_HIDE_QUOTAS", "").lower() in ("1", "true", "yes"):
        config["show_quotas"] = False
    elif os.environ.get("STATUSLINE_SHOW_QUOTAS", "").lower() in ("0", "false", "no"):
        config["show_quotas"] = False

    if (os.environ.get("STATUSLINE_HIDE_COST", "").lower() in ("1", "true", "yes") or
        os.environ.get("STATUSLINE_HIDE_PRICE", "").lower() in ("1", "true", "yes")):
        config["show_cost"] = False
    elif (os.environ.get("STATUSLINE_SHOW_COST", "").lower() in ("0", "false", "no") or
          os.environ.get("STATUSLINE_SHOW_PRICE", "").lower() in ("0", "false", "no")):
        config["show_cost"] = False

    # Check alias in config file
    if "show_price" in config:
        config["show_cost"] = config["show_price"]

    # 3. CLI arguments
    parser = argparse.ArgumentParser(description="Antigravity CLI Statusline HUD")
    parser.add_argument("--no-quotas", "--hide-quotas", "--payg", "--pay-as-you-go",
                        dest="no_quotas", action="store_true",
                        help="Disable 5h and weekly quota segments (pay-as-you-go mode)")
    parser.add_argument("--no-cost", "--hide-cost", "--no-price", "--hide-price",
                        dest="no_cost", action="store_true",
                        help="Disable estimated session cost / price segment")
    parser.add_argument("--no-git", dest="no_git", action="store_true",
                        help="Disable Git branch segment")
    parser.add_argument("--no-dir", dest="no_dir", action="store_true",
                        help="Disable working directory segment")

    args, _ = parser.parse_known_args()
    if args.no_quotas:
        config["show_quotas"] = False
    if args.no_cost:
        config["show_cost"] = False
    if args.no_git:
        config["show_git"] = False
    if args.no_dir:
        config["show_dir"] = False

    return config

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    cfg = load_config()

    # 1. Model & reasoning effort
    model_obj = data.get("model", {})
    raw_name = model_obj.get("display_name") or model_obj.get("id") or "Gemini"
    clean_name = re.sub(r"\s*\([^)]*\)$", "", raw_name)
    effort = model_obj.get("effort")
    effort_abbr = {"low": "low", "medium": "med", "high": "high"}.get(str(effort).lower(), effort)
    if effort:
        model_text = f"󰚩 {clean_name} ({effort_abbr})"
    else:
        model_text = f"󰚩 {clean_name}"

    # 2. Context window
    ctx = data.get("context_window", {})
    used_pct = ctx.get("used_percentage", 0.0)
    ctx_size = ctx.get("context_window_size", 0)
    size_str = format_tokens(ctx_size) if ctx_size else ""
    ctx_text = f"󰍛 {used_pct:.1f}%/{size_str}" if size_str else f"󰍛 {used_pct:.1f}%"

    if used_pct < 40:
        ctx_bg = "#bb9af7" # Purple
    elif used_pct < 75:
        ctx_bg = "#e0af68" # Orange
    else:
        ctx_bg = "#f7768e" # Red alert

    # 3. Total tokens (using unit 'tk')
    total_in = ctx.get("total_input_tokens", 0)
    total_out = ctx.get("total_output_tokens", 0)
    tot_tokens = total_in + total_out
    tokens_text = f"󰈚 {format_tokens(tot_tokens)} tk"

    # 4. Estimated cost
    curr_usage = ctx.get("current_usage", {})
    cache_in = curr_usage.get("cache_read_input_tokens", 0)
    cost = estimate_cost(clean_name, total_in, total_out, cache_in)
    cost_text = f"󰠠 {format_cost(cost)}"

    # 5. Quotas (only evaluated if enabled)
    quota_5h_text = None
    q5h_bg = "#9ece6a"
    quota_w_text = None
    qw_bg = "#7dcfff"

    if cfg.get("show_quotas", True):
        quotas = data.get("quota", {})
        # 5h quota (Nerd Font icon: 󰔛 timer)
        q5h = quotas.get("gemini-5h", {})
        rem_5h = q5h.get("remaining_fraction")
        reset_5h = q5h.get("reset_in_seconds", 0)
        if rem_5h is not None:
            rem_5h_pct = int(rem_5h * 100)
            dur_5h = format_duration(reset_5h)
            quota_5h_text = f"󰔛 5h: {rem_5h_pct}% (~{dur_5h})"
            if rem_5h > 0.5:
                q5h_bg = "#9ece6a" # Green
            elif rem_5h > 0.2:
                q5h_bg = "#e0af68" # Orange
            else:
                q5h_bg = "#f7768e" # Red

        # Weekly quota
        qw = quotas.get("gemini-weekly", {})
        rem_w = qw.get("remaining_fraction")
        if rem_w is not None:
            rem_w_pct = int(rem_w * 100)
            quota_w_text = f"󰔚 Hebdo: {rem_w_pct}%"
            if rem_w > 0.5:
                qw_bg = "#7dcfff" # Cyan
            elif rem_w > 0.2:
                qw_bg = "#e0af68" # Orange
            else:
                qw_bg = "#f7768e" # Red

    # 6. Directory & Git branch
    cwd = data.get("cwd") or (data.get("workspace") or {}).get("current_dir") or ""
    dir_text = f" {shorten_path(cwd)}" if (cwd and cfg.get("show_dir", True)) else None

    git_text = None
    git_bg = "#ff9e64"
    if cwd and cfg.get("show_git", True):
        git_info = get_git_info(cwd)
        if git_info:
            branch, is_dirty = git_info
            dirty_flag = " *" if is_dirty else ""
            git_text = f" {branch}{dirty_flag}"
            git_bg = "#ff9e64" if not is_dirty else "#f7768e"

    # Assemble Powerline segments:
    # [(text, bg_hex, fg_hex)]
    segments = [
        (model_text, "#7aa2f7", "#15161e"),
        (ctx_text, ctx_bg, "#15161e"),
        (tokens_text, "#2ac3de", "#15161e"),
    ]

    if cfg.get("show_cost", True):
        segments.append((cost_text, "#73daca", "#15161e"))

    if quota_5h_text:
        segments.append((quota_5h_text, q5h_bg, "#15161e"))

    if quota_w_text:
        segments.append((quota_w_text, qw_bg, "#15161e"))

    if dir_text:
        segments.append((dir_text, "#24283b", "#c0caf5"))

    if git_text:
        segments.append((git_text, git_bg, "#15161e"))

    # Render Powerline
    SEP = ""
    out = []
    for i, (text, bg, fg) in enumerate(segments):
        br, bg_g, bb = hex_to_rgb(bg)
        fr, fg_g, fb = hex_to_rgb(fg)
        out.append(f"\033[48;2;{br};{bg_g};{bb}m\033[38;2;{fr};{fg_g};{fb}m {text} ")

        if i + 1 < len(segments):
            next_bg = segments[i + 1][1]
            nbr, nbg_g, nbb = hex_to_rgb(next_bg)
            out.append(f"\033[48;2;{nbr};{nbg_g};{nbb}m\033[38;2;{br};{bg_g};{bb}m{SEP}")
        else:
            out.append(f"\033[49m\033[38;2;{br};{bg_g};{bb}m{SEP}\033[0m")

    sys.stdout.write("".join(out))

if __name__ == "__main__":
    main()
