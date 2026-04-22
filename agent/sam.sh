#!/usr/bin/env bash
# SAM Local Testing Commands for Agent
# Usage: ./sam.sh <command>
# Prerequisites: Docker Desktop running, .env file configured
#
# Commands:
#   ./sam.sh validate     Validate SAM template
#   ./sam.sh build        Build SAM dependencies
#   ./sam.sh test-first   Test with first_question.json
#   ./sam.sh test-history Test with question_with_history.json
#
# Windows/Docker Notes:
#   - set -e: Exit immediately on error (avoids silent failures with Docker on Windows)
#   - set -a && source .env && set +a: Load .env vars before SAM commands
#     (Windows Docker often needs explicit env vars loaded, not inherited)

set -e
set -a && source .env && set +a

SAM="${SAM_CMD:-sam}"

case "${1}" in
  validate)
    "$SAM" validate
    ;;
  build)
    "$SAM" build --use-container
    ;;
  test-first)
    "$SAM" local invoke TripAssistantAgentFunction --event tests/events/first_question.json
    ;;
  test-history)
    "$SAM" local invoke TripAssistantAgentFunction --event tests/events/question_with_history.json
    ;;
  *)
    echo "Usage: ./invoke_local.sh <command>"
    echo ""
    echo "Commands:"
    echo "  validate      Validate SAM template"
    echo "  build         Build SAM dependencies"
    echo "  test-first    Test with first_question.json"
    echo "  test-history  Test with question_with_history.json"
    ;;
esac
