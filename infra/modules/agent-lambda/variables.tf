variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "ssm_parameter_arn" {
  description = "ARN of the SSM parameter containing the OpenAI API key"
  type        = string
}

variable "ssm_parameter_name" {
  description = "Name of the SSM parameter containing the OpenAI API key"
  type        = string
}
