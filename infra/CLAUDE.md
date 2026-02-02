# Infrastructure Service

AWS infrastructure using Terraform. Optimized for FREE tier / minimal cost.

## Architecture

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  CloudFront  │────▶│     S3      │     │   Lambda     │
│    (CDN)     │     │ (frontend)  │     │ (API+Agent)  │
└──────────────┘     └─────────────┘     └──────┬───────┘
                                                │
┌──────────────┐     ┌─────────────┐            │
│  API Gateway │────▶│   Lambda    │◀───────────┘
│   (HTTP)     │     │  (handler)  │
└──────────────┘     └─────────────┘
                            │
                     ┌──────┴───────┐
                     │  Parameter   │
                     │   Store      │
                     │ (API keys)   │
                     └──────────────┘
```

## AWS Services (Cheap Stack)

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Lambda | API + Agent | 1M requests/month |
| API Gateway | HTTP API | 1M requests/month |
| S3 | Frontend hosting | 5GB storage |
| CloudFront | CDN | 1TB transfer/month |
| Parameter Store | Secrets | FREE (standard) |
| CloudWatch | Logs | 5GB logs |

**Estimated cost: $0-5/month**

## Key Files

```
infra/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── s3-cloudfront/        # Static site hosting
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── lambda-api-gateway/   # Serverless API
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ssm/                  # Parameter Store secrets
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    └── dev/
        ├── main.tf
        ├── terraform.tfvars
        └── backend.tf
```

## Resources Created

### lambda-api-gateway module
- Lambda function: `trip-assistant-api-{env}`
- Runtime: Python 3.11
- Architecture: ARM64 (cheaper)
- Memory: 512MB
- Timeout: 30s
- HTTP API Gateway with routes:
  - `POST /api/messages`
  - `GET /api/health`

### s3-cloudfront module
- S3 bucket: `trip-assistant-frontend-{env}`
- CloudFront distribution
- HTTPS with default certificate
- SPA routing (404 → index.html)

### ssm module
- Parameter: `/trip-assistant/{env}/openai-api-key`

## Deploy Commands

```bash
cd infra/environments/dev

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Destroy everything (cleanup)
terraform destroy
```

## Variables

```hcl
variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
  default     = "dev"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
```

## Outputs

```hcl
output "api_url" {
  description = "API Gateway endpoint URL"
  value       = module.lambda-api-gateway.api_url
}

output "frontend_url" {
  description = "CloudFront distribution URL"
  value       = module.s3-cloudfront.cloudfront_url
}

output "s3_bucket" {
  description = "S3 bucket for frontend deployment"
  value       = module.s3-cloudfront.bucket_name
}
```

## Deployment Workflow

### First-time setup
```bash
# 1. Configure AWS credentials
aws configure

# 2. Create terraform.tfvars
cd infra/environments/dev
cat > terraform.tfvars << EOF
environment    = "dev"
openai_api_key = "sk-..."
aws_region     = "us-east-1"
EOF

# 3. Initialize and apply
terraform init
terraform apply
```

### Deploy frontend updates
```bash
cd frontend
npm run build

# Sync to S3
aws s3 sync dist/ s3://trip-assistant-frontend-dev --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

### Deploy API updates
```bash
cd api
pip install -e . -t package/
cp -r app package/
cd package && zip -r ../lambda.zip .

aws lambda update-function-code \
  --function-name trip-assistant-api-dev \
  --zip-file fileb://lambda.zip
```

## Cost Optimization Tips

1. **HTTP API Gateway** (not REST) - 70% cheaper
2. **Lambda ARM64** - 20% cheaper than x86
3. **us-east-1 region** - Often cheapest for Lambda
4. **Parameter Store Standard** - FREE (vs Secrets Manager $0.40/secret)
5. **CloudFront free tier** - 1TB/month is plenty
6. **No NAT Gateway** - Lambda accesses internet directly
7. **No custom domain** - Use CloudFront default URL

## CORS Configuration

```hcl
cors_configuration {
  allow_origins = ["https://*.cloudfront.net"]
  allow_methods = ["POST", "GET", "OPTIONS"]
  allow_headers = ["Content-Type"]
  max_age       = 300
}
```

## Monitoring

```bash
# Lambda logs
aws logs tail /aws/lambda/trip-assistant-api-dev --follow
```
