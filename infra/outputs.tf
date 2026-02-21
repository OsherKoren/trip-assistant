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

output "frontend_url" {
  description = "CloudFront distribution URL for frontend"
  value       = module.s3_cloudfront.cloudfront_url
}

output "frontend_s3_bucket" {
  description = "S3 bucket name for frontend deployment"
  value       = module.s3_cloudfront.s3_bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = module.s3_cloudfront.cloudfront_distribution_id
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID for frontend"
  value       = module.cognito.user_pool_client_id
}

output "cognito_user_pool_domain" {
  description = "Cognito-hosted domain for OAuth endpoints"
  value       = module.cognito.user_pool_domain
}
