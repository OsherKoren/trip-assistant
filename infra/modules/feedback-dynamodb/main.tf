# --- DynamoDB Table for Feedback ---

resource "aws_dynamodb_table" "feedback" {
  name         = "${var.project_name}-feedback-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "message_id"

  attribute {
    name = "message_id"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
