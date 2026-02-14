output "parameter_arn" {
  description = "ARN of the OpenAI API key SSM parameter"
  value       = aws_ssm_parameter.openai_api_key.arn
}

output "parameter_name" {
  description = "Name of the OpenAI API key SSM parameter"
  value       = aws_ssm_parameter.openai_api_key.name
}
