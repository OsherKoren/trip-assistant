# --- IAM Role ---

resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-agent-${var.environment}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# CloudWatch Logs permissions
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# SSM Parameter Store read access for API key
resource "aws_iam_role_policy" "ssm_read" {
  name = "${var.project_name}-agent-${var.environment}-ssm"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ssm:GetParameter"
        Resource = var.ssm_parameter_arn
      }
    ]
  })
}

# --- Lambda Function ---

resource "aws_lambda_function" "agent" {
  function_name = "${var.project_name}-agent-${var.environment}"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.11"
  architectures = ["arm64"]
  handler       = "handler.handler"
  memory_size   = 512
  timeout       = 30

  # Placeholder — actual code deployed separately
  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  environment {
    variables = {
      SSM_PARAMETER_NAME = var.ssm_parameter_name
      ENVIRONMENT        = var.environment
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- CloudWatch Log Group ---

resource "aws_cloudwatch_log_group" "agent" {
  name              = "/aws/lambda/${aws_lambda_function.agent.function_name}"
  retention_in_days = 7

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
