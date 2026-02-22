# --- DynamoDB Table for Feedback ---

resource "aws_dynamodb_table" "feedback" {
  name         = "${var.project_name}-feedback-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  range_key    = "created_at"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
