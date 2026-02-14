# Infrastructure Service

AWS infrastructure using Terraform. Optimized for FREE tier / minimal cost.

## Architecture

```
┌──────────────┐     ┌─────────────┐
│  CloudFront  │────▶│     S3      │
│    (CDN)     │     │ (frontend)  │
└──────────────┘     └─────────────┘

┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  API Gateway │────▶│ API Lambda  │────▶│ Agent Lambda  │
│   (HTTP)     │     │ (container) │     │ (container)   │
└──────────────┘     └──────┬──────┘     └──────┬────────┘
                            │                    │
                     ┌──────▼──────┐      ┌──────▼───────┐
                     │  ECR Repo   │      │  Parameter   │
                     │  (images)   │      │   Store      │
                     └─────────────┘      └──────────────┘

GitHub Actions (OIDC) ──▶ Build ARM64 image ──▶ Push to ECR ──▶ Update Lambda
```

## Deployment Model

**Container image Lambdas** — both services deploy as Docker images via ECR:
- CI workflows (`agent-ci.yml`, `api-ci.yml`) run tests + quality checks only
- `deploy.yml` builds ARM64 images, pushes to ECR, updates Lambda, publishes version, updates alias
- `infra-ci.yml` validates Terraform on PR, applies on merge to main
- Uses GitHub OIDC for AWS auth (no static keys)
- Automatic rollback on smoke test failure

## AWS Services (Cheap Stack)

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| Lambda (x2) | API + Agent (container images) | 1M requests/month |
| ECR (x2) | Docker image repos | 500MB storage |
| API Gateway | HTTP API | 1M requests/month |
| S3 | Frontend hosting | 5GB storage |
| CloudFront | CDN | 1TB transfer/month |
| Parameter Store | Secrets | FREE (standard) |
| CloudWatch | Logs | 5GB logs |

**Estimated cost: $0-5/month**

## Key Files

```
infra/
├── TASKS.md              # Development task tracking
├── main.tf               # Root module — wires all modules together
├── variables.tf          # Root input variables
├── outputs.tf            # Root outputs (api_url, function names, ECR URLs)
├── .gitignore            # Ignores .terraform/, *.tfstate*, *.tfvars, *.zip
└── modules/
    ├── ssm/              # Parameter Store for OpenAI API key
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── ecr/              # ECR repositories for container images
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── agent-lambda/     # Agent Lambda function + IAM
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── api-lambda/       # API Lambda function + IAM
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── api-gateway/      # HTTP API Gateway
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── github-oidc/      # GitHub Actions OIDC auth + IAM
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── s3-cloudfront/    # Static site hosting (planned)
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Resources Created

### ssm module
- Parameter: `/trip-assistant/{env}/openai-api-key` (SecureString)

### ecr module
- ECR repository: `trip-assistant-agent-{env}` (immutable tags, keep last 10)
- ECR repository: `trip-assistant-api-{env}` (immutable tags, keep last 10)

### agent-lambda module
- Lambda function: `trip-assistant-agent-{env}` (container image)
- IAM role with CloudWatch Logs + SSM GetParameter
- Package type: Image (from ECR), 512MB, 30s timeout
- Lambda alias `live` (CD pipeline manages versions)
- CloudWatch log group (7-day retention)

### api-lambda module
- Lambda function: `trip-assistant-api-{env}` (container image)
- IAM role with CloudWatch Logs + lambda:InvokeFunction (agent)
- Package type: Image (from ECR), 512MB, 30s timeout
- Lambda alias `live` (CD pipeline manages versions)
- CloudWatch log group (7-day retention)

### github-oidc module
- OIDC provider for GitHub Actions
- IAM role with Lambda deploy + ECR push permissions
- Scoped to `main` branch of the repository

### api-gateway module
- HTTP API Gateway: `trip-assistant-{env}`
- Lambda proxy integration (payload v2.0)
- Catch-all `$default` route (FastAPI handles routing)
- Auto-deploy stage
- CORS: allow all origins (dev)

### s3-cloudfront module (planned)
- S3 bucket: `trip-assistant-frontend-{env}`
- CloudFront distribution
- HTTPS with default certificate
- SPA routing (404 → index.html)

## Deploy Commands

```bash
cd infra

# Set OpenAI API key (lives only in your shell session, not written to disk)
export TF_VAR_openai_api_key="sk-proj-your-actual-key"

# Initialize Terraform (first time or after module changes)
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# View outputs (API URL, function names)
terraform output

# Smoke test
curl https://<api_url>/api/health

# Destroy everything (cleanup)
terraform destroy
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `environment` | `dev` | Environment name (dev, prod) |
| `aws_region` | `us-east-2` | AWS region |
| `project_name` | `trip-assistant` | Project name for resource naming |
| `openai_api_key` | — | OpenAI API key (sensitive, pass via `TF_VAR_openai_api_key`) |

## Outputs

| Output | Description |
|--------|-------------|
| `api_url` | API Gateway endpoint URL |
| `agent_lambda_function_name` | Agent Lambda function name |
| `api_lambda_function_name` | API Lambda function name |
| `agent_ecr_repository_url` | ECR repository URL for agent images |
| `api_ecr_repository_url` | ECR repository URL for API images |
| `github_actions_role_arn` | IAM role ARN for GitHub Actions OIDC |
| `frontend_url` | CloudFront distribution URL (planned) |
| `s3_bucket` | S3 bucket for frontend deployment (planned) |

## Cost Optimization Tips

1. **HTTP API Gateway** (not REST) — 70% cheaper
2. **Lambda ARM64** — 20% cheaper than x86
3. **us-east-2 region** — Consistent pricing
4. **Parameter Store Standard** — FREE (vs Secrets Manager $0.40/secret)
5. **No NAT Gateway** — Lambda accesses internet directly
6. **No custom domain** — Use API Gateway / CloudFront default URLs
7. **CloudFront free tier** — 1TB/month is plenty

## Monitoring

```bash
# Agent Lambda logs
aws logs tail /aws/lambda/trip-assistant-agent-dev --follow

# API Lambda logs
aws logs tail /aws/lambda/trip-assistant-api-dev --follow
```

## Rollback

| Method | Speed | How |
|--------|-------|-----|
| Automatic (smoke fail) | ~10s | deploy.yml reverts alias to previous version |
| Manual CLI | ~10s | `aws lambda update-alias --function-version N` |
| Git revert + redeploy | ~3min | Revert commit triggers new image build + deploy |

## Future Additions (Not Yet Deployed)

- S3 + CloudFront for frontend hosting
- Custom domain + ACM certificate
- Remote state backend (S3 + DynamoDB locking)
- Production environment
