#!/usr/bin/env bash
# SAM Local Testing Commands
# Usage: ./sam.sh <command>
# Prerequisites: Docker Desktop running, .env file configured
#
# Commands:
#   ./sam.sh validate   Validate SAM template
#   ./sam.sh build      Build SAM dependencies
#   ./sam.sh start      Start local Lambda API server (port 3001)
#   ./sam.sh dev        Start local FastAPI server with agent (port 8000)
#   ./sam.sh health     GET /api/health
#   ./sam.sh test       POST a test question to /api/messages
#
# Workflows:
#   Lambda:  validate -> build -> start (terminal 1) -> health/test (terminal 2)
#   Dev:     dev (terminal 1) -> health/test (terminal 2)

set -e

SAM="${SAM_CMD:-sam}"

case "${1}" in
  validate)
    "$SAM" validate
    ;;
  build)
    "$SAM" build --use-container
    ;;
  start)
    "$SAM" local start-api
    ;;
  dev)
    set -a && source .env && set +a
    uv run fastapi dev app/main.py
    ;;
  health)
    curl -s http://localhost:8000/api/health | python -m json.tool
    ;;
  test)
    curl -s -X POST http://localhost:8000/api/messages \
      -H "Content-Type: application/json" \
      -d '{"question": "What car did we rent?"}' | python -m json.tool
    ;;
  *)
    echo "Usage: ./sam.sh <command>"
    echo ""
    echo "Commands:"
    echo "  validate   Validate SAM template"
    echo "  build      Build SAM dependencies"
    echo "  start      Start local Lambda API server (port 3001)"
    echo "  dev        Start local FastAPI server with agent (port 8000)"
    echo "  health     GET /api/health"
    echo "  test       POST a test question to /api/messages"
    ;;
esac
