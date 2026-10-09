#!/usr/bin/env python3
"""
Test runner for antigravity-statusline.
Simulates payloads from Antigravity CLI and displays the rendered statusline.
"""

import json
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATUSLINE_BIN = os.path.join(SCRIPT_DIR, "statusline.py")

PAYLOADS = [
    {
        "description": "Standard session with moderate context and active quotas",
        "data": {
            "cwd": os.path.expanduser("~"),
            "model": {"display_name": "Gemini 3.8 Flash (Medium)", "effort": "medium"},
            "context_window": {
                "total_input_tokens": 95669,
                "total_output_tokens": 21611,
                "context_window_size": 1048576,
                "used_percentage": 11.2,
                "current_usage": {"cache_read_input_tokens": 85527}
            },
            "quota": {
                "gemini-5h": {"remaining_fraction": 0.698, "reset_in_seconds": 14224},
                "gemini-weekly": {"remaining_fraction": 0.785, "reset_in_seconds": 301971}
            }
        }
    },
    {
        "description": "Heavy session (high context, low quota, in git repo)",
        "data": {
            "cwd": SCRIPT_DIR,
            "model": {"display_name": "Gemini 3.1 Pro (High)", "effort": "high"},
            "context_window": {
                "total_input_tokens": 820000,
                "total_output_tokens": 65000,
                "context_window_size": 1048576,
                "used_percentage": 84.4,
                "current_usage": {"cache_read_input_tokens": 700000}
            },
            "quota": {
                "gemini-5h": {"remaining_fraction": 0.15, "reset_in_seconds": 1800},
                "gemini-weekly": {"remaining_fraction": 0.35, "reset_in_seconds": 86400}
            }
        }
    }
]

def run_test():
    print("Testing antigravity-statusline rendering:\n")
    for i, test in enumerate(PAYLOADS, 1):
        print(f"--- Scenario {i}: {test['description']} ---")
        p = subprocess.Popen([STATUSLINE_BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(json.dumps(test["data"]).encode("utf-8"))
        print(out.decode("utf-8", errors="replace"))
        print("\n")
    print("All scenarios rendered successfully.")

if __name__ == "__main__":
    run_test()
