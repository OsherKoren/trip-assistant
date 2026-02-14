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

- [ ] Create `infra/environments/dev/terraform.tfvars` (gitignored)
  - [ ] Set `environment`, `aws_region`, `openai_api_key`
- [ ] Run `terraform apply` — create all resources
- [ ] Verify outputs: `terraform output` shows `api_url`
- [ ] Smoke test: `curl <api_url>/api/health` returns 200
- [ ] Document deployment steps in `infra/CLAUDE.md`

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

## Completion Criteria

- [ ] All 5 modules created and validated (SSM, Agent Lambda, API Lambda, API Gateway, root)
- [ ] `terraform validate` passes
- [ ] `terraform plan` shows expected resources
- [ ] Infrastructure deployed and health check returns 200
- [ ] Ready for code deployment pipeline (future task)

---

## Future Tasks (Not in Scope)

- [ ] S3 + CloudFront for frontend hosting
- [ ] CI/CD pipeline for code deployment to Lambda
- [ ] Custom domain + ACM certificate
- [ ] Remote state backend (S3 + DynamoDB locking)
- [ ] Production environment (`environments/prod/`)
