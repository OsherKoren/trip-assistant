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

variable "frontend_url" {
  description = "Frontend URL for CORS origin restriction"
  type        = string
}

variable "ecr_image_uri" {
  description = "ECR image URI for the API Lambda function"
  type        = string
}

variable "feedback_table_name" {
  description = "DynamoDB table name for feedback storage"
  type        = string
  default     = ""
}

variable "feedback_table_arn" {
  description = "DynamoDB table ARN for feedback storage (for IAM permissions)"
  type        = string
  default     = ""
}

variable "feedback_email" {
  description = "Email address for SES feedback notifications"
  type        = string
  default     = ""
}
