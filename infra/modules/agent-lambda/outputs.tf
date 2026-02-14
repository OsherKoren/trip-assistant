output "function_name" {
  description = "Agent Lambda function name"
  value       = aws_lambda_function.agent.function_name
}

output "function_arn" {
  description = "Agent Lambda function ARN"
  value       = aws_lambda_function.agent.arn
}

output "invoke_arn" {
  description = "Agent Lambda invoke ARN"
  value       = aws_lambda_function.agent.invoke_arn
}
