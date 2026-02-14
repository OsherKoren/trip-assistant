# --- OIDC Provider for GitHub Actions ---

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- IAM Role for GitHub Actions CD ---

resource "aws_iam_role" "github_actions" {
  name = "${var.project_name}-github-actions-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.github_repo}:ref:refs/heads/main",
              "repo:${var.github_repo}:pull_request",
            ]
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Lambda Deployment Policy ---

resource "aws_iam_role_policy" "lambda_deploy" {
  name = "${var.project_name}-lambda-deploy-${var.environment}"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:PublishVersion",
          "lambda:UpdateAlias",
          "lambda:GetAlias",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
        ]
        Resource = [
          var.agent_lambda_arn,
          "${var.agent_lambda_arn}:*",
          var.api_lambda_arn,
          "${var.api_lambda_arn}:*",
        ]
      },
      {
        Effect   = "Allow"
        Action   = "apigateway:GET"
        Resource = "*"
      }
    ]
  })
}

# --- Terraform CI/CD Policy (state + infrastructure management) ---

resource "aws_iam_role_policy" "terraform" {
  name = "${var.project_name}-terraform-${var.environment}"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # State backend access
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-terraform-state",
          "arn:aws:s3:::${var.project_name}-terraform-state/*",
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
        ]
        Resource = "arn:aws:dynamodb:${var.aws_region}:*:table/${var.project_name}-terraform-locks"
      },
      # IAM — manage Lambda execution roles and policies
      {
        Effect = "Allow"
        Action = [
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:GetRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:ListInstanceProfilesForRole",
          "iam:PassRole",
          "iam:GetOpenIDConnectProvider",
          "iam:TagOpenIDConnectProvider",
        ]
        Resource = [
          "arn:aws:iam::*:role/${var.project_name}-*",
          "arn:aws:iam::*:oidc-provider/token.actions.githubusercontent.com",
        ]
      },
      # Lambda — full management for plan/apply
      {
        Effect = "Allow"
        Action = [
          "lambda:*",
        ]
        Resource = [
          "arn:aws:lambda:${var.aws_region}:*:function:${var.project_name}-*",
        ]
      },
      # CloudWatch Logs — manage log groups
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:ListTagsForResource",
          "logs:TagResource",
          "logs:PutRetentionPolicy",
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.project_name}-*"
      },
      # SSM — manage parameters
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:PutParameter",
          "ssm:DeleteParameter",
          "ssm:ListTagsForResource",
          "ssm:AddTagsToResource",
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/*"
      },
      {
        Effect   = "Allow"
        Action   = "ssm:DescribeParameters"
        Resource = "*"
      },
      # API Gateway — manage HTTP APIs (IAM uses apigateway: prefix for v2)
      {
        Effect = "Allow"
        Action = [
          "apigateway:*",
        ]
        Resource = "*"
      },
      # ECR — manage repositories
      {
        Effect = "Allow"
        Action = [
          "ecr:DescribeRepositories",
          "ecr:ListTagsForResource",
          "ecr:GetLifecyclePolicy",
          "ecr:GetRepositoryPolicy",
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:*:repository/${var.project_name}-*",
        ]
      },
    ]
  })
}

# --- ECR Push/Pull Policy ---

resource "aws_iam_role_policy" "ecr_push" {
  name = "${var.project_name}-ecr-push-${var.environment}"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
        ]
        Resource = [
          var.agent_ecr_arn,
          var.api_ecr_arn,
        ]
      }
    ]
  })
}
