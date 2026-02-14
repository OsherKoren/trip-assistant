variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for the agent Lambda invocation"
  type        = string
}

variable "agent_lambda_function_name" {
  description = "Name of the agent Lambda function to invoke"
  type        = string
}

variable "agent_lambda_arn" {
  description = "ARN of the agent Lambda function (for IAM permissions)"
  type        = string
}
