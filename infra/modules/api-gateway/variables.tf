variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "api_lambda_invoke_arn" {
  description = "Invoke ARN of the API Lambda function"
  type        = string
}

variable "api_lambda_function_name" {
  description = "Name of the API Lambda function (for permission grant)"
  type        = string
}

variable "api_lambda_alias_name" {
  description = "Name of the API Lambda alias (for permission qualifier)"
  type        = string
}

variable "cognito_user_pool_endpoint" {
  description = "Cognito User Pool endpoint (issuer URL for JWT validation)"
  type        = string
}

variable "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID (audience for JWT validation)"
  type        = string
}

variable "cognito_smoke_test_client_id" {
  description = "Cognito Smoke Test Client ID (audience for JWT validation)"
  type        = string
}

variable "frontend_url" {
  description = "Frontend URL for CORS origin restriction (e.g. CloudFront URL)"
  type        = string
}
