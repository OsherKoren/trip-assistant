variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of the API Lambda alias (for REST API integration URI)"
  type        = string
}

variable "lambda_function_name" {
  description = "API Lambda function name (for Lambda permission)"
  type        = string
}

variable "lambda_alias_name" {
  description = "API Lambda alias name (for Lambda permission qualifier)"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN (for COGNITO_USER_POOLS authorizer)"
  type        = string
}

variable "frontend_url" {
  description = "CloudFront URL of the frontend (used as CORS allowed origin)"
  type        = string
}
