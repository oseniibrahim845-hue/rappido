#!/bin/sh
# Log a sent email, show the next one, commit and push: sh step.sh <lead_id> <email> <message_id>
set -e
cd "$(dirname "$0")"
python3 -W ignore log_send.py "$1" "$2" "$3" "$3"
python3 next.py
cd ../.. && git add -A shopify-leads && git commit -qm "Outreach day 4 progress

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01R5gXYQek1J6Kb2P6BuuFjU" && git push -q -u origin claude/laughing-newton-h4hz9g
