# Infrastructure Service - Development Tasks

> **Note**: This file tracks development progress and is kept in version control
> as a reference for project workflow. It is NOT part of the production infrastructure.
> Each service in the monorepo has its own TASKS.md for independent tracking.

## Overview

Terraform infrastructure for deploying the agent and API services to AWS Lambda with API Gateway.

**Target Architecture**:
```
API Gateway (HTTP API)
    │
    ├── POST /api/messages  ──▶  API Lambda  ──▶  Agent Lambda
    ├── GET  /api/health    ──▶  API Lambda
    │
SSM Parameter Store ── OPENAI_API_KEY ──▶ Agent Lambda
```

**Scope**: Agent Lambda + API Lambda + API Gateway + SSM. Frontend (S3/CloudFront) deferred.

---

## Phase 1: Project Setup & Provider Configuration ✅

Set up Terraform project structure, provider, backend, and variables.

- [x] Create `infra/main.tf` — root module
  - [x] Configure `terraform` block with `required_version >= 1.5`
  - [x] Configure `aws` provider with region from variable
  - [x] Configure S3 backend for remote state (commented out for initial local state)
- [x] Create `infra/variables.tf` — root-level input variables
  - [x] `environment` (string, default "dev")
  - [x] `aws_region` (string, default "us-east-2")
  - [x] `project_name` (string, default "trip-assistant")
- [x] Create `infra/outputs.tf` — root-level outputs (empty for now)
- [x] Create `infra/.gitignore` — ignore `.terraform/`, `*.tfstate*`, `*.tfvars`
- [x] Validate: `terraform init && terraform validate && terraform fmt -check`

---

## Phase 2: SSM Parameter Store Module ✅

Store the OpenAI API key securely using SSM Parameter Store (free tier).

- [x] Create `infra/modules/ssm/main.tf`
  - [x] `aws_ssm_parameter` resource for OpenAI API key
    - Name: `/${var.project_name}/${var.environment}/openai-api-key`
    - Type: `SecureString`
    - Value: from variable (sensitive)
- [x] Create `infra/modules/ssm/variables.tf`
  - [x] `project_name`, `environment`, `openai_api_key` (sensitive)
- [x] Create `infra/modules/ssm/outputs.tf`
  - [x] Output `parameter_arn` and `parameter_name`
- [x] Wire SSM module in `infra/main.tf`
  - [x] Add `openai_api_key` to root `variables.tf` (sensitive)
  - [x] Add module block calling `./modules/ssm`
- [x] Validate: `terraform validate && terraform fmt -check`
- [ ] Dry-run: `terraform plan` (requires AWS credentials, preview only)

---

## Phase 3: Agent Lambda Module ✅

Deploy the LangGraph agent as a standalone Lambda function.

- [x] Create `infra/modules/agent-lambda/main.tf`
  - [x] IAM role + policy for Lambda execution
    - Basic execution role (CloudWatch Logs)
    - SSM `GetParameter` permission for the API key parameter
  - [x] `aws_lambda_function` resource
    - Function name: `${var.project_name}-agent-${var.environment}`
    - Runtime: `python3.11`
    - Architecture: `arm64`
    - Handler: `handler.handler` (placeholder, TBD for real agent entry point)
    - Memory: 512MB, Timeout: 30s
    - Environment variables: `SSM_PARAMETER_NAME`, `ENVIRONMENT`
    - Placeholder zip for initial deployment (actual code deployed separately)
  - [x] `aws_cloudwatch_log_group` with 7-day retention
- [x] Create `infra/modules/agent-lambda/variables.tf`
  - [x] `project_name`, `environment`, `ssm_parameter_arn`, `ssm_parameter_name`
- [x] Create `infra/modules/agent-lambda/outputs.tf`
  - [x] Output `function_name`, `function_arn`, `invoke_arn`
- [x] Wire Agent Lambda module in `infra/main.tf`
  - [x] Pass SSM outputs to agent-lambda module
- [x] Validate: `terraform validate && terraform fmt -check`
- [ ] Dry-run: `terraform plan`

---

## Phase 4: API Lambda Module ✅

Deploy the FastAPI API as a Lambda function behind API Gateway.

- [x] Create `infra/modules/api-lambda/main.tf`
  - [x] IAM role + policy for Lambda execution
    - Basic execution role (CloudWatch Logs)
    - `lambda:InvokeFunction` permission on Agent Lambda ARN
  - [x] `aws_lambda_function` resource
    - Function name: `${var.project_name}-api-${var.environment}`
    - Runtime: `python3.11`
    - Architecture: `arm64`
    - Handler: `app.handler.handler` (Mangum)
    - Memory: 512MB, Timeout: 30s
    - Environment variables:
      - `ENVIRONMENT=prod`
      - `AGENT_LAMBDA_FUNCTION_NAME` from agent lambda output
      - `AWS_LAMBDA_EXEC_WRAPPER_REGION`
    - Placeholder zip for initial deployment
  - [x] `aws_cloudwatch_log_group` with 7-day retention
- [x] Create `infra/modules/api-lambda/variables.tf`
  - [x] `project_name`, `environment`, `aws_region`, `agent_lambda_function_name`, `agent_lambda_arn`
- [x] Create `infra/modules/api-lambda/outputs.tf`
  - [x] Output `function_name`, `function_arn`, `invoke_arn`
- [x] Wire API Lambda module in `infra/main.tf`
  - [x] Pass agent lambda outputs to api-lambda module
- [x] Validate: `terraform validate && terraform fmt -check`
- [ ] Dry-run: `terraform plan`

---

## Phase 5: API Gateway Module ✅

Create HTTP API Gateway that routes requests to the API Lambda.

- [x] Create `infra/modules/api-gateway/main.tf`
  - [x] `aws_apigatewayv2_api` — HTTP API
    - Name: `${var.project_name}-${var.environment}`
    - Protocol: HTTP
    - CORS: allow all origins for dev (restrict later)
  - [x] `aws_apigatewayv2_integration` — Lambda proxy integration
  - [x] `aws_apigatewayv2_route` — catch-all `$default` route
    (API Gateway forwards all paths to FastAPI, which handles routing)
  - [x] `aws_apigatewayv2_stage` — `$default` stage with auto-deploy
  - [x] `aws_lambda_permission` — allow API Gateway to invoke API Lambda
- [x] Create `infra/modules/api-gateway/variables.tf`
  - [x] `project_name`, `environment`, `api_lambda_invoke_arn`, `api_lambda_function_name`
- [x] Create `infra/modules/api-gateway/outputs.tf`
  - [x] Output `api_url` (the invoke URL)
- [x] Wire API Gateway module in `infra/main.tf`
  - [x] Pass API Lambda outputs to api-gateway module
- [x] Update root `infra/outputs.tf`
  - [x] Output `api_url` from api-gateway module
  - [x] Output `agent_lambda_function_name`
  - [x] Output `api_lambda_function_name`
- [x] Validate: `terraform validate && terraform fmt -check`
- [ ] Dry-run: `terraform plan`

---

## Phase 6: Deploy & Verify

Apply infrastructure and verify with real AWS resources.

- [x] ~~Create `infra/environments/dev/terraform.tfvars`~~ — Not needed; CI/CD uses `TF_VAR_` env vars
- [x] Run `terraform apply` — applied via `infra-ci.yml` on merge to main
- [x] Verify outputs: `terraform output` shows `api_url`
- [x] Smoke test: `curl <api_url>/api/health` returns 200
- [x] Document deployment steps in `infra/CLAUDE.md`

---

## Validation Strategy

Terraform validation is different from Python testing. Here's what replaces tests at each phase:

| Check | What It Catches | When to Run |
|-------|----------------|-------------|
| `terraform fmt -check` | Formatting issues (like ruff) | Every phase |
| `terraform validate` | Syntax errors, missing refs (like mypy) | Every phase |
| `terraform plan` | Resource config errors, dependency issues | Every phase (requires AWS creds) |
| `terraform apply` | Real deployment errors | Phase 6 only |
| `curl` smoke test | End-to-end connectivity | After apply |

**No manual AWS console checking needed** — `terraform plan` and `terraform output` are the verification tools.

---

## Phase 7: ECR Repositories ✅

Container image registries for Lambda deployment.

- [x] Create `infra/modules/ecr/` module
  - [x] Two repositories: `trip-assistant-agent-{env}`, `trip-assistant-api-{env}`
  - [x] Immutable tags, lifecycle policy (keep last 10), force_delete for dev
- [x] Wire ECR module in `infra/main.tf`
- [x] Add ECR repository URL outputs

---

## Phase 8: Container Image Lambdas ✅

Switch from ZIP-based to container image deployment.

- [x] Replace zip config with `package_type = "Image"` + `image_uri` in agent-lambda module
- [x] Replace zip config with `package_type = "Image"` + `image_uri` in api-lambda module
- [x] Add `lifecycle { ignore_changes = [image_uri] }` — CD pipeline manages images
- [x] Wire ECR image URIs from root `main.tf`
- [x] Validate: `terraform validate` passes

---

## Phase 9: GitHub OIDC + ECR Permissions ✅

OIDC auth for GitHub Actions with ECR push access.

- [x] Create `infra/modules/github-oidc/` with OIDC provider + IAM role
- [x] Lambda deploy policy (UpdateFunctionCode, PublishVersion, UpdateAlias)
- [x] ECR push policy (GetAuthorizationToken, PutImage, etc.)
- [x] Lambda aliases (`live`) on both functions with `publish = true`
- [x] API Gateway wired to alias ARN

---

## Phase 10: Agent Lambda Handler + Dockerfile ✅

Lambda entry point and container image for the agent.

- [x] `agent/handler.py` — Lambda entry point with lazy SSM fetch
- [x] `agent/tests/test_handler.py` — 7 passing tests (refactored to monkeypatch/mocker)
- [x] `agent/Dockerfile` — Updated with `awslambdaric` entrypoint
- [x] `agent/pyproject.toml` — Added `awslambdaric` dependency

---

## Phase 11: CI/CD Workflows ✅

Deployment pipeline and infrastructure CI.

- [x] `.github/workflows/deploy.yml` — Build + push + deploy (OIDC, ARM64, rollback)
- [x] `.github/workflows/infra-ci.yml` — Terraform fmt/validate/plan on PR, apply on merge
- [x] Clean up `agent-ci.yml` — Removed deploy jobs (build-docker, push-to-ecr, create-release)
- [x] Clean up `api-ci.yml` — Removed deploy jobs (build-docker, push-to-ecr, create-release)

---

## Phase 12: Remote State Backend ✅

S3 + DynamoDB backend for shared Terraform state, enabling CI/CD apply.

- [x] Create `infra/bootstrap/` — one-time setup for state infrastructure
  - [x] S3 bucket (`trip-assistant-terraform-state`) — versioned, encrypted, public access blocked
  - [x] DynamoDB table (`trip-assistant-terraform-locks`) — pay-per-request
- [x] Apply bootstrap locally (`terraform apply` in `infra/bootstrap/`)
- [x] Uncomment S3 backend in `infra/main.tf`
- [x] Migrate local state to S3 (`terraform init -migrate-state`)
- [x] Re-enable apply job in `infra-ci.yml`

---

## Phase 13: CI/CD Fixes ✅

Fix deploy workflow and OIDC issues discovered after first merge.

- [x] Add `provenance: false` to `docker/build-push-action` (fix OCI manifest error)
- [x] Use short SHA tags (7 chars) + `latest` for ECR images
- [x] Switch ECR to mutable tags (allows `latest` overwrites)
- [x] Add `pull_request` claim to OIDC trust policy (fix PR workflow auth)
- [x] Add `apigatewayv2:GetApis` permission for smoke test

---

## Phase 14: Full-Chain Smoke Test ✅

End-to-end deploy validation covering the entire Lambda chain.

- [x] Add `__ping__` sentinel in `agent/handler.py` — exercises SSM + LangGraph init, skips OpenAI
- [x] Add 2 ping tests in `agent/tests/test_handler.py`
- [x] Add "Full chain ping" step in `deploy.yml` — POSTs to `/api/messages`, validates full chain
- [x] Exclude `agent/tests/**` and `api/tests/**` from deploy workflow trigger

---

## Completion Criteria

- [x] All modules created and validated (SSM, ECR, Agent Lambda, API Lambda, API Gateway, OIDC)
- [x] `terraform validate` passes
- [x] Remote state backend configured (S3 + DynamoDB)
- [x] CI/CD pipeline configured (deploy.yml + infra-ci.yml)
- [x] `terraform plan` shows expected resources
- [x] Infrastructure deployed and health check returns 200
- [x] Full-chain smoke test validates API Gateway → API Lambda → Agent Lambda

---

## Phase 15: S3 + CloudFront for Frontend Hosting

Add static hosting infrastructure for the React frontend.

**Architecture**: `S3 (static) → CloudFront (CDN) → User Browser`

### Task 15.1: Create S3 + CloudFront module
- [x] Create `infra/modules/s3-cloudfront/variables.tf`
  - [x] `project_name` (string)
  - [x] `environment` (string)
- [x] Create `infra/modules/s3-cloudfront/main.tf`
  - [x] S3 bucket: `${project_name}-frontend-${environment}`
    - Block ALL public access (CloudFront-only via OAC)
    - Server-side encryption (AES256)
    - Tags: Project, Environment
  - [x] CloudFront Origin Access Control (OAC)
    - Signing behavior: `always`, protocol: `sigv4`
  - [x] CloudFront distribution
    - Origin: S3 bucket with OAC
    - Default root object: `index.html`
    - Custom error response: 403/404 → `/index.html` (SPA routing)
    - Viewer protocol policy: `redirect-to-https`
    - Cache policy: `CachingOptimized` (managed policy)
    - Price class: `PriceClass_100` (cheapest — US/EU only)
    - Default CloudFront certificate (no custom domain yet)
  - [x] S3 bucket policy: Allow CloudFront OAC `s3:GetObject` only
- [x] Create `infra/modules/s3-cloudfront/outputs.tf`
  - [x] `s3_bucket_name` — for deployment workflow
  - [x] `s3_bucket_arn` — for IAM policy
  - [x] `cloudfront_distribution_id` — for cache invalidation
  - [x] `cloudfront_distribution_arn` — for IAM policy
  - [x] `cloudfront_url` — the `https://dXXX.cloudfront.net` URL

### Task 15.2: Wire module in root configuration
- [x] Add `module "s3_cloudfront"` block in `infra/main.tf`
  - [x] Pass `project_name` and `environment`
- [x] Add root outputs in `infra/outputs.tf`
  - [x] `frontend_url` → CloudFront URL
  - [x] `frontend_s3_bucket` → S3 bucket name
  - [x] `cloudfront_distribution_id` → for deploy workflow

### Task 15.3: Update GitHub OIDC permissions
- [x] Add `frontend_s3_bucket_arn` and `cloudfront_distribution_arn` variables to `modules/github-oidc/variables.tf`
- [x] Pass new variables from root `main.tf` to `github_oidc` module
- [x] Add new IAM policy in `modules/github-oidc/main.tf`
  - [x] S3 deploy: `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`, `s3:GetObject` on frontend bucket
  - [x] CloudFront: `cloudfront:CreateInvalidation`, `cloudfront:GetInvalidation` on distribution
- [x] Add S3/CloudFront management permissions to Terraform CI/CD policy
  - [x] S3: bucket and object management for `${project_name}-frontend-*`
  - [x] CloudFront: distribution management

### Task 15.4: Validate and commit
- [x] `terraform fmt -recursive`
- [x] `terraform validate`
- [ ] Commit phase 15 changes

---

## Phase 16: Frontend Deployment Workflow

GitHub Actions workflow to build and deploy frontend to S3/CloudFront.

### Task 16.1: Create frontend deploy workflow
- [x] Create `.github/workflows/frontend-deploy.yml`
  - [x] Trigger: push to `main`, paths `frontend/**`
  - [x] Job 1: Detect Changes (`dorny/paths-filter`)
  - [x] Job 2: Build & Deploy
    - [x] Checkout, setup Node 20, `npm ci`, `npm run build`
    - [x] Configure AWS credentials (OIDC, same role as deploy.yml)
    - [x] `aws s3 sync dist/ s3://$BUCKET --delete`
    - [x] `aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"`
  - [x] Job 3: Smoke Test
    - [x] `curl` CloudFront URL returns 200
    - [x] Verify response contains HTML content

### Task 16.2: Commit and verify
- [ ] Commit phase 16 changes
- [ ] Merge to main → infra-ci applies Terraform → frontend-deploy deploys app
- [ ] Verify CloudFront URL serves the React app

---

## Phase 17: Cognito Authentication (Google + Email/Password)

Add user authentication using AWS Cognito. Industry-standard pattern for mid-size organizations.
Free tier covers 50,000 MAU — more than enough for 5 family members.

**Architecture**:
```
User opens CloudFront URL
  → React login page (Google sign-in button + email/password form)
  → Cognito authenticates → returns JWT token
  → Browser stores token → sends with every API request
  → API Gateway validates JWT → rejects unauthorized requests
```

**Social Login**: Google (free). Apple Sign-In deferred (requires $99/year Apple Developer Program).

### Task 17.1: Create Cognito module
- [ ] Create `infra/modules/cognito/variables.tf`
  - [ ] `project_name` (string)
  - [ ] `environment` (string)
  - [ ] `callback_urls` (list of strings — CloudFront URL + localhost for dev)
  - [ ] `logout_urls` (list of strings)
  - [ ] `google_client_id` (string, sensitive)
  - [ ] `google_client_secret` (string, sensitive)
- [ ] Create `infra/modules/cognito/main.tf`
  - [ ] `aws_cognito_user_pool`
    - Name: `${project_name}-${environment}`
    - Email as sign-in alias (family members sign in with email)
    - Password policy: minimum 8 chars (keep it simple for family)
    - Auto-verified attributes: email
    - Account recovery: email only (no SMS — free)
    - Tags: Project, Environment
  - [ ] `aws_cognito_user_pool_domain`
    - Cognito-hosted domain: `${project_name}-${environment}` (free, no custom domain needed)
  - [ ] `aws_cognito_identity_provider` (Google)
    - Provider type: Google
    - Client ID + secret from variables
    - Attribute mapping: email, name
    - Scopes: `openid`, `email`, `profile`
  - [ ] `aws_cognito_user_pool_client`
    - Name: `${project_name}-frontend-${environment}`
    - Supported identity providers: `COGNITO` + `Google`
    - Allowed OAuth flows: `code` (authorization code grant — most secure)
    - Allowed OAuth scopes: `openid`, `email`, `profile`
    - Callback URLs: from variable (CloudFront URL + localhost)
    - Logout URLs: from variable
    - No client secret (public client — SPA can't keep secrets)
    - Token validity: access token 1 hour, refresh token 30 days
- [ ] Create `infra/modules/cognito/outputs.tf`
  - [ ] `user_pool_id` — for API Gateway authorizer
  - [ ] `user_pool_arn` — for IAM policies
  - [ ] `user_pool_client_id` — for React frontend config
  - [ ] `user_pool_endpoint` — Cognito issuer URL for JWT validation
  - [ ] `user_pool_domain` — for hosted UI / OAuth endpoints

### Task 17.2: Add API Gateway JWT authorizer
- [ ] Update `infra/modules/api-gateway/variables.tf`
  - [ ] Add `cognito_user_pool_endpoint` (string)
  - [ ] Add `cognito_user_pool_client_id` (string)
- [ ] Update `infra/modules/api-gateway/main.tf`
  - [ ] Add `aws_apigatewayv2_authorizer` — JWT type
    - Issuer: Cognito user pool endpoint
    - Audience: user pool client ID
  - [ ] Update `aws_apigatewayv2_route` to use the authorizer
    - Protect `$default` route with JWT authorizer
  - [ ] Add new route: `GET /api/health` — **no** authorizer (for smoke tests)

### Task 17.3: Wire Cognito module in root configuration
- [ ] Add `google_client_id` and `google_client_secret` to root `variables.tf` (sensitive)
- [ ] Add `module "cognito"` block in `infra/main.tf`
  - [ ] Pass variables + callback/logout URLs using CloudFront output
- [ ] Pass Cognito outputs to `api-gateway` module
- [ ] Add root outputs in `infra/outputs.tf`
  - [ ] `cognito_user_pool_id`
  - [ ] `cognito_user_pool_client_id`
  - [ ] `cognito_user_pool_domain`

### Task 17.4: Update GitHub OIDC permissions
- [ ] Add Cognito management permissions to Terraform CI/CD policy in `modules/github-oidc/main.tf`
  - [ ] `cognito-idp:*` scoped to project user pools

### Task 17.5: Create family user accounts
- [ ] After `terraform apply`, create 5 user accounts via CLI:
  ```bash
  aws cognito-idp admin-create-user --user-pool-id <pool-id> --username <email>
  ```
  - [ ] Or family members self-register via Google sign-in (no manual creation needed)

### Task 17.6: Validate and commit
- [ ] `terraform fmt -recursive`
- [ ] `terraform validate`
- [ ] Commit phase 17 changes

---

## Phase 18: Frontend Auth Integration

Add login/logout flow to the React frontend using Cognito.

> **Note**: Tracked here for dependency clarity. Detailed tasks in `frontend/TASKS.md`.

- [ ] Install `@aws-amplify/auth` (lightweight — just the auth module, not all of Amplify)
- [ ] Add Cognito config (User Pool ID, Client ID, domain) from Terraform outputs
- [ ] Add login page with Google sign-in button + email/password form
- [ ] Add auth context/provider — protect routes, redirect to login if unauthenticated
- [ ] Attach JWT token to API requests (`Authorization: Bearer <token>`)
- [ ] Add logout button
- [ ] Test on mobile browser (iPhone/Samsung) and desktop

---

## Completion Criteria (Updated)

- [x] Phases 1-14: Backend infrastructure deployed and operational
- [ ] Phase 15: S3 + CloudFront module created and applied
- [ ] Phase 16: Frontend deployment workflow operational
- [ ] Phase 17: Cognito authentication with Google + email/password
- [ ] Phase 18: Frontend login flow integrated
- [ ] CloudFront URL serves the React chat interface with login

---

## Future Tasks (Not in Scope)

- [ ] Apple Sign-In (requires $99/year Apple Developer Program)
- [ ] Custom domain + ACM certificate
- [ ] Production environment (`environments/prod/`)
