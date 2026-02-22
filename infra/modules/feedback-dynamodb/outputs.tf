output "table_arn" {
  description = "ARN of the feedback DynamoDB table"
  value       = aws_dynamodb_table.feedback.arn
}

output "table_name" {
  description = "Name of the feedback DynamoDB table"
  value       = aws_dynamodb_table.feedback.name
}
