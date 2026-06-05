#!/bin/bash
# Run this script in a terminal on the Pi (via RustDesk).
set -e
cd ~/guardrail
git pull
~/.local/bin/uv sync
echo "Pi is up to date."
