# --- IAM Role ---

resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-api-${var.environment}-role"

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

# Invoke Agent Lambda permission
resource "aws_iam_role_policy" "invoke_agent" {
  name = "${var.project_name}-api-${var.environment}-invoke-agent"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = var.agent_lambda_arn
      }
    ]
  })
}

# --- Lambda Function ---

resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api-${var.environment}"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.11"
  architectures = ["arm64"]
  handler       = "app.handler.handler"
  memory_size   = 512
  timeout       = 30

  # Placeholder — actual code deployed separately
  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  environment {
    variables = {
      ENVIRONMENT                    = "prod"
      AGENT_LAMBDA_FUNCTION_NAME     = var.agent_lambda_function_name
      AWS_LAMBDA_EXEC_WRAPPER_REGION = var.aws_region
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- CloudWatch Log Group ---

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 7

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
