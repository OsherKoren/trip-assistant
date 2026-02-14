variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository (owner/repo) for OIDC trust policy"
  type        = string
}

variable "agent_lambda_arn" {
  description = "ARN of the agent Lambda function"
  type        = string
}

variable "api_lambda_arn" {
  description = "ARN of the API Lambda function"
  type        = string
}

variable "agent_ecr_arn" {
  description = "ARN of the agent ECR repository"
  type        = string
}

variable "api_ecr_arn" {
  description = "ARN of the API ECR repository"
  type        = string
}
