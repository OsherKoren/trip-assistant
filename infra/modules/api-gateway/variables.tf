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
