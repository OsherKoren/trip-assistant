# --- HTTP API Gateway ---

resource "aws_apigatewayv2_api" "api" {
  name          = "${var.project_name}-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [var.frontend_url]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Lambda Integration ---

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.api_lambda_invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# --- JWT Authorizer (Cognito) ---

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.api.id
  authorizer_type  = "JWT"
  name             = "cognito-jwt"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    issuer   = var.cognito_user_pool_endpoint
    audience = [var.cognito_user_pool_client_id, var.cognito_smoke_test_client_id]
  }
}

# --- Health Check Route (no auth — for smoke tests) ---

resource "aws_apigatewayv2_route" "health" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /api/health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# --- Protected Routes (JWT auth) ---
# Use explicit method routes instead of $default so that OPTIONS preflight
# requests are handled by the cors_configuration block (no auth required).

resource "aws_apigatewayv2_route" "post" {
  api_id             = aws_apigatewayv2_api.api.id
  route_key          = "POST /api/messages"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "post_feedback" {
  api_id             = aws_apigatewayv2_api.api.id
  route_key          = "POST /api/feedback"
  target             = "integrations/${aws_apigatewayv2_integration.lambda.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# --- Default Stage (auto-deploy) ---

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 10
    throttling_rate_limit  = 5
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Lambda Permission ---

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.api_lambda_function_name
  qualifier     = var.api_lambda_alias_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
