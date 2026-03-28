# --- DynamoDB Table for Question Cache ---

resource "aws_dynamodb_table" "cache" {
  name         = "${var.project_name}-cache-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "question_hash"

  attribute {
    name = "question_hash"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
