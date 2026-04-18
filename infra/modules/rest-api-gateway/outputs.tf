output "api_url" {
  description = "REST API Gateway invoke URL (includes stage)"
  value       = aws_api_gateway_stage.api.invoke_url
}

output "rest_api_id" {
  description = "REST API ID"
  value       = aws_api_gateway_rest_api.api.id
}

output "stage_name" {
  description = "Stage name"
  value       = aws_api_gateway_stage.api.stage_name
}
