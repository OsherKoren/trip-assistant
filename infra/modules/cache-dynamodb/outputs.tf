output "table_arn" {
  description = "ARN of the cache DynamoDB table"
  value       = aws_dynamodb_table.cache.arn
}

output "table_name" {
  description = "Name of the cache DynamoDB table"
  value       = aws_dynamodb_table.cache.name
}
