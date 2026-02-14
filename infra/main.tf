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
}

module "api_gateway" {
  source = "./modules/api-gateway"

  project_name             = var.project_name
  environment              = var.environment
  api_lambda_invoke_arn    = module.api_lambda.alias_invoke_arn
  api_lambda_function_name = module.api_lambda.function_name
  api_lambda_alias_name    = module.api_lambda.alias_name
}

module "github_oidc" {
  source = "./modules/github-oidc"

  project_name     = var.project_name
  environment      = var.environment
  github_repo      = var.github_repo
  agent_lambda_arn = module.agent_lambda.function_arn
  api_lambda_arn   = module.api_lambda.function_arn
  agent_ecr_arn    = module.ecr.agent_repository_arn
  api_ecr_arn      = module.ecr.api_repository_arn
}
