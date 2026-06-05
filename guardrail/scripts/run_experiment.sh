#!/bin/bash
# Usage: bash run_experiment.sh <condition>  (A | B | C | D)
set -e
CONDITION="${1:?Usage: run_experiment.sh <A|B|C|D>}"
export GUARDRAIL_EXPERIMENT="$CONDITION"

AUDIT_LOG=~/guardrail/guardrail-audit.jsonl
> "$AUDIT_LOG"   # reset log

echo "Starting experiment condition $CONDITION..."
cd ~/sandbox/project
claude
