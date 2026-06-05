#!/bin/bash
set -e
PI_HOST="${PI_HOST:-pi@raspberrypi.local}"
ssh "$PI_HOST" "cd ~/guardrail && git pull && ~/.local/bin/uv sync"
