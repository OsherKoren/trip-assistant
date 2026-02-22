output "user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "Cognito User Pool ARN"
  value       = aws_cognito_user_pool.main.arn
}

output "user_pool_client_id" {
  description = "Cognito User Pool Client ID for the frontend"
  value       = aws_cognito_user_pool_client.frontend.id
}

output "user_pool_endpoint" {
  description = "Cognito User Pool endpoint (issuer URL for JWT validation)"
  value       = "https://${aws_cognito_user_pool.main.endpoint}"
}

output "user_pool_domain" {
  description = "Cognito-hosted domain for OAuth endpoints"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "smoke_test_client_id" {
  description = "Client ID for CI/CD smoke test (client credentials grant)"
  value       = aws_cognito_user_pool_client.smoke_test.id
}

output "smoke_test_client_secret" {
  description = "Client secret for CI/CD smoke test"
  value       = aws_cognito_user_pool_client.smoke_test.client_secret
  sensitive   = true
}

output "token_endpoint" {
  description = "Cognito OAuth2 token endpoint"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com/oauth2/token"
}
