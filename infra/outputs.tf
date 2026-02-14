output "api_url" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_url
}

output "agent_lambda_function_name" {
  description = "Agent Lambda function name"
  value       = module.agent_lambda.function_name
}

output "api_lambda_function_name" {
  description = "API Lambda function name"
  value       = module.api_lambda.function_name
}
