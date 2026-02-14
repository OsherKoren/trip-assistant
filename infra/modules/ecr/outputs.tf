output "agent_repository_url" {
  description = "ECR repository URL for the agent image"
  value       = aws_ecr_repository.agent.repository_url
}

output "api_repository_url" {
  description = "ECR repository URL for the API image"
  value       = aws_ecr_repository.api.repository_url
}

output "agent_repository_arn" {
  description = "ECR repository ARN for the agent image"
  value       = aws_ecr_repository.agent.arn
}

output "api_repository_arn" {
  description = "ECR repository ARN for the API image"
  value       = aws_ecr_repository.api.arn
}
