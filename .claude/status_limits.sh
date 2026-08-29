#!/bin/bash

# Status line script to show model, usage, daily and weekly application limits
# Usage: .claude/status_limits.sh [daily_limit] [weekly_limit]

DAILY_LIMIT=${1:-10}
WEEKLY_LIMIT=${2:-50}
DATA_FILE="data/job_evaluations.json"

# Get model name from settings or environment
MODEL="${CLAUDE_MODEL:-haiku}"
if [ -f ".claude/settings.local.json" ]; then
  MODEL=$(jq -r '.model // "haiku"' ".claude/settings.local.json" 2>/dev/null || echo "haiku")
fi
if [ -f ".claude/settings.json" ]; then
  MODEL=$(jq -r '.model // "'$MODEL'"' ".claude/settings.json" 2>/dev/null || echo "$MODEL")
fi

# Extract model short name (opus, sonnet, haiku, fable)
MODEL_SHORT=$(echo "$MODEL" | grep -oE '(opus|sonnet|haiku|fable)' | head -1)
if [ -z "$MODEL_SHORT" ]; then
  MODEL_SHORT="claude"
fi

# Get thinking status
THINKING="off"
if [ -f ".claude/settings.local.json" ]; then
  THINKING=$(jq -r 'if .alwaysThinkingEnabled == true then "on" elif .alwaysThinkingEnabled == false then "off" else "auto" end' ".claude/settings.local.json" 2>/dev/null || echo "auto")
fi
if [ -f ".claude/settings.json" ] && [ "$THINKING" = "auto" ]; then
  THINKING=$(jq -r 'if .alwaysThinkingEnabled == true then "on" elif .alwaysThinkingEnabled == false then "off" else "auto" end' ".claude/settings.json" 2>/dev/null || echo "auto")
fi

# Get effort level
EFFORT="med"
if [ -f ".claude/settings.local.json" ]; then
  EFFORT=$(jq -r '.effortLevel // "med"' ".claude/settings.local.json" 2>/dev/null | sed 's/medium/med/g; s/xhigh/xh/g; s/high/hi/g; s/low/lo/g')
fi
if [ "$EFFORT" = "med" ] || [ -z "$EFFORT" ]; then
  if [ -f ".claude/settings.json" ]; then
    EFFORT=$(jq -r '.effortLevel // "med"' ".claude/settings.json" 2>/dev/null | sed 's/medium/med/g; s/xhigh/xh/g; s/high/hi/g; s/low/lo/g')
  fi
fi
EFFORT=${EFFORT:-med}

# Get token usage from environment (set by Claude Code)
if [ -n "$CLAUDE_TOKEN_USAGE" ]; then
  USAGE_PERCENT=$(echo "$CLAUDE_TOKEN_USAGE" | awk '{printf "%.0f", $1}')
  USAGE_DISPLAY="$USAGE_PERCENT%"
else
  USAGE_DISPLAY="?"
fi

# Get counts from today and this week
if [ -f "$DATA_FILE" ]; then
  # Count entries from today (since midnight)
  TODAY_START=$(date +%s -d "00:00:00" 2>/dev/null || date -v-0d +%s)
  TODAY_COUNT=$(jq "[.evaluations[]? | select(.timestamp | tonumber > $TODAY_START)] | length" "$DATA_FILE" 2>/dev/null || echo "0")

  # Count entries from this week (last 7 days)
  WEEK_START=$(date +%s -d "7 days ago" 2>/dev/null || date -v-7d +%s)
  WEEK_COUNT=$(jq "[.evaluations[]? | select(.timestamp | tonumber > $WEEK_START)] | length" "$DATA_FILE" 2>/dev/null || echo "0")
else
  TODAY_COUNT=0
  WEEK_COUNT=0
fi

# Get git branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "no-git")

# Format output: branch | model thinking effort | usage | daily | weekly | time
echo "$BRANCH | $MODEL_SHORT 🧠$THINKING $EFFORT | $USAGE_DISPLAY | D:$TODAY_COUNT/$DAILY_LIMIT W:$WEEK_COUNT/$WEEKLY_LIMIT | $(date '+%H:%M')"
