terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "trip-assistant-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "trip-assistant-terraform-locks"
    encrypt        = true
    use_lockfile   = true
  }
}

provider "aws" {
  region = var.aws_region
}

# --- Modules ---

module "ssm" {
  source = "./modules/ssm"

  project_name   = var.project_name
  environment    = var.environment
  openai_api_key = var.openai_api_key
}

module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
}

module "agent_lambda" {
  source = "./modules/agent-lambda"

  project_name       = var.project_name
  environment        = var.environment
  ssm_parameter_arn  = module.ssm.parameter_arn
  ssm_parameter_name = module.ssm.parameter_name
  ecr_image_uri      = "${module.ecr.agent_repository_url}:initial"
}

module "api_lambda" {
  source = "./modules/api-lambda"

  project_name               = var.project_name
  environment                = var.environment
  aws_region                 = var.aws_region
  agent_lambda_function_name = "${module.agent_lambda.function_name}:${module.agent_lambda.alias_name}"
  agent_lambda_arn           = module.agent_lambda.function_arn
  ecr_image_uri              = "${module.ecr.api_repository_url}:initial"
  frontend_url               = module.s3_cloudfront.cloudfront_url
  feedback_table_name        = module.feedback_dynamodb.table_name
  feedback_table_arn         = module.feedback_dynamodb.table_arn
  feedback_email             = var.feedback_email
}

module "api_gateway" {
  source = "./modules/api-gateway"

  project_name                 = var.project_name
  environment                  = var.environment
  api_lambda_invoke_arn        = module.api_lambda.alias_invoke_arn
  api_lambda_function_name     = module.api_lambda.function_name
  api_lambda_alias_name        = module.api_lambda.alias_name
  cognito_user_pool_endpoint   = module.cognito.user_pool_endpoint
  cognito_user_pool_client_id  = module.cognito.user_pool_client_id
  cognito_smoke_test_client_id = module.cognito.smoke_test_client_id
  frontend_url                 = module.s3_cloudfront.cloudfront_url
}

module "s3_cloudfront" {
  source = "./modules/s3-cloudfront"

  project_name = var.project_name
  environment  = var.environment
}

module "cognito" {
  source = "./modules/cognito"

  project_name         = var.project_name
  environment          = var.environment
  aws_region           = var.aws_region
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret

  callback_urls = [
    "https://${module.s3_cloudfront.cloudfront_domain_name}/",
    "http://localhost:5173/",
  ]
  logout_urls = [
    "https://${module.s3_cloudfront.cloudfront_domain_name}/",
    "http://localhost:5173/",
  ]
}

module "feedback_dynamodb" {
  source = "./modules/feedback-dynamodb"

  project_name = var.project_name
  environment  = var.environment
}

module "ses" {
  source = "./modules/ses"

  feedback_email = var.feedback_email
}

module "github_oidc" {
  source = "./modules/github-oidc"

  project_name                = var.project_name
  environment                 = var.environment
  aws_region                  = var.aws_region
  github_repo                 = var.github_repo
  agent_lambda_arn            = module.agent_lambda.function_arn
  api_lambda_arn              = module.api_lambda.function_arn
  agent_ecr_arn               = module.ecr.agent_repository_arn
  api_ecr_arn                 = module.ecr.api_repository_arn
  frontend_s3_bucket_arn      = module.s3_cloudfront.s3_bucket_arn
  cloudfront_distribution_arn = module.s3_cloudfront.cloudfront_distribution_arn
}
