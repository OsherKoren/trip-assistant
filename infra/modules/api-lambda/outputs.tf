output "function_name" {
  description = "API Lambda function name"
  value       = aws_lambda_function.api.function_name
}

output "function_arn" {
  description = "API Lambda function ARN"
  value       = aws_lambda_function.api.arn
}

output "invoke_arn" {
  description = "API Lambda invoke ARN"
  value       = aws_lambda_function.api.invoke_arn
}

output "alias_invoke_arn" {
  description = "API Lambda alias invoke ARN"
  value       = aws_lambda_alias.live.invoke_arn
}

output "alias_name" {
  description = "API Lambda alias name"
  value       = aws_lambda_alias.live.name
}
