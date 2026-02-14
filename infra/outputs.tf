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

output "agent_ecr_repository_url" {
  description = "ECR repository URL for agent images"
  value       = module.ecr.agent_repository_url
}

output "api_ecr_repository_url" {
  description = "ECR repository URL for API images"
  value       = module.ecr.api_repository_url
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions OIDC"
  value       = module.github_oidc.github_actions_role_arn
}
