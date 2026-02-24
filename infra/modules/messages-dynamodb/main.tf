# --- DynamoDB Table for Messages ---

resource "aws_dynamodb_table" "messages" {
  name         = "${var.project_name}-messages-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
