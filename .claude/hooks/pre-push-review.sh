#!/bin/bash
# Pre-push review hook: blocks git push until review skills have been run.
# After reviews are done, Claude creates a marker file, and the next push succeeds.

MARKER=".claude/.reviews-done"

# If reviews were already completed, allow the push
if [ -f "$MARKER" ]; then
    rm -f "$MARKER"
    exit 0
fi

# Determine which files changed compared to main
CHANGED=$(git diff --name-only origin/main...HEAD 2>/dev/null)
if [ -z "$CHANGED" ]; then
    # Fallback: compare with last commit
    CHANGED=$(git diff --name-only HEAD~1 2>/dev/null)
fi

# If no changes detected, allow push
if [ -z "$CHANGED" ]; then
    exit 0
fi

# Determine which skills to run
SKILLS="/review-python"
SECURITY="security-review"

if echo "$CHANGED" | grep -q "^agent/"; then
    SKILLS="$SKILLS, /review-langgraph"
fi

if echo "$CHANGED" | grep -q "^api/"; then
    SKILLS="$SKILLS, /review-fastapi"
fi

# Block the push and instruct Claude
cat >&2 <<EOF
PUSH BLOCKED - Code reviews required before pushing.

Changed services detected from diff against main:
$(echo "$CHANGED" | sed 's/^/  /')

Please run the following review skills in order:
  1. $SKILLS
  2. $SECURITY (check for vulnerabilities, secrets, injection risks)

After all reviews pass, create the marker file:
  touch .claude/.reviews-done

Then retry the push.
EOF

exit 2
