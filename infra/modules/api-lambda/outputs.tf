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
