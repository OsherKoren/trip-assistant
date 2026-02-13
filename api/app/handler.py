"""AWS Lambda handler for the Trip Assistant API.

This module provides the Lambda handler that wraps the FastAPI application
using Mangum, allowing the API to be deployed as an AWS Lambda function
behind API Gateway.

Architecture:
    API Gateway → Lambda (this handler) → FastAPI (app) → Agent

Usage:
    In Lambda configuration, set handler to: app.handler.handler
    The handler processes API Gateway HTTP API (v2.0) events and returns
    formatted responses that API Gateway can forward to clients.
"""

from mangum import Mangum

from app.main import app

# Lambda handler - wraps FastAPI app for AWS Lambda execution
# Mangum translates API Gateway events to ASGI requests and ASGI responses back to API Gateway format
handler = Mangum(app)
