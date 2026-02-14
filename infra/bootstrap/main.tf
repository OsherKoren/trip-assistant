# --- Terraform State Backend Bootstrap ---
#
# Run ONCE to create the S3 bucket and DynamoDB table for remote state.
# This config uses local state (stored in bootstrap/.terraform/).
#
# Usage:
#   cd infra/bootstrap
#   terraform init
#   terraform apply
#
# After this succeeds, uncomment the backend block in infra/main.tf
# and run: terraform init -migrate-state

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- S3 Bucket for Terraform State ---

resource "aws_s3_bucket" "state" {
  bucket = "${var.project_name}-terraform-state"

  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Project = var.project_name
    Purpose = "Terraform state"
  }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket = aws_s3_bucket.state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- DynamoDB Table for State Locking ---

resource "aws_dynamodb_table" "locks" {
  name         = "${var.project_name}-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Project = var.project_name
    Purpose = "Terraform state locking"
  }
}
