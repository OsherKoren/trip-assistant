#!/bin/bash
# Pre-push review hook: blocks git push until review skills have been run.
# Claude Code passes JSON on stdin with tool_input.command.

# Read JSON input from stdin, extract command using python (jq not available)
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Only act on git push commands
if ! echo "$COMMAND" | grep -q "git push"; then
    exit 0
fi

MARKER=".claude/.reviews-done"

# If reviews were already completed, allow the push
if [ -f "$MARKER" ]; then
    rm -f "$MARKER"
    exit 0
fi

# Determine which files changed compared to main
CHANGED=$(git diff --name-only origin/main...HEAD 2>/dev/null)
if [ -z "$CHANGED" ]; then
    CHANGED=$(git diff --name-only HEAD~1 2>/dev/null)
fi

# If no changes detected, allow push
if [ -z "$CHANGED" ]; then
    exit 0
fi

# Determine which skills to run
SKILLS="/review-python"

if echo "$CHANGED" | grep -q "^agent/"; then
    SKILLS="$SKILLS, /review-langgraph"
fi

if echo "$CHANGED" | grep -q "^api/"; then
    SKILLS="$SKILLS, /review-fastapi"
fi

# Build the deny reason
read -r -d '' REASON <<REASON_EOF
PUSH BLOCKED - Code reviews required before pushing.

Changed services detected from diff against main:
$(echo "$CHANGED" | sed 's/^/  /')

Please run the following review skills in order:
  1. $SKILLS
  2. security-review (check for vulnerabilities, secrets, injection risks)

After all reviews pass, create the marker file:
  touch .claude/.reviews-done

Then retry the push.
REASON_EOF

# Escape the reason for JSON output using python
REASON_JSON=$(echo "$REASON" | python -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")

# Output JSON deny decision to block the push
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": $REASON_JSON
  }
}
EOF
