resource "aws_ssm_parameter" "openai_api_key" {
  name        = "/${var.project_name}/${var.environment}/openai-api-key"
  description = "OpenAI API key for the trip assistant agent"
  type        = "SecureString"
  value       = var.openai_api_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
