#!/usr/bin/env bash
# =============================================================================
# create-smoke-test-user.sh
#
# One-time setup: creates the CI/CD smoke test user in the Cognito user pool.
# Run this manually after `terraform apply` has created the user pool.
#
# The smoke test user allows GitHub Actions deploy.yml to authenticate as a
# real Cognito user (via admin-initiate-auth) and call /api/messages with a
# real question — proving the full pipeline works after every deployment.
#
# Prerequisites:
#   - AWS CLI configured with credentials that have cognito-idp permissions
#   - Terraform has already been applied (user pool must exist)
#     To apply Terraform, export the required vars first:
#       export TF_VAR_google_client_id="..."        # from Google Cloud Console → APIs & Services → Credentials
#       export TF_VAR_google_client_secret="..."    # same OAuth 2.0 client
#       export TF_VAR_openai_api_key="..."          # from platform.openai.com
#     Then: cd infra && terraform plan -out=tfplan && terraform apply tfplan
#
# Usage:
#   SMOKE_PASSWORD="your-chosen-password" bash infra/scripts/create-smoke-test-user.sh
#
# After running, add these two secrets to GitHub → repo → Settings → Secrets:
#   SMOKE_TEST_USERNAME = smoke-test-user
#   SMOKE_TEST_PASSWORD = <the password you chose>
# =============================================================================

set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-2}"
USERNAME="smoke-test-user"
PASSWORD="${SMOKE_PASSWORD:?Set SMOKE_PASSWORD env var to your chosen password}"

POOL_ID=$(aws cognito-idp list-user-pools --max-results 20 \
  --query "UserPools[?Name=='trip-assistant-dev'].Id" \
  --output text --region "$AWS_REGION")

if [ -z "$POOL_ID" ]; then
  echo "ERROR: Could not find Cognito user pool 'trip-assistant-dev'"
  exit 1
fi

echo "Creating user '$USERNAME' in pool $POOL_ID ..."
aws cognito-idp admin-create-user \
  --user-pool-id "$POOL_ID" \
  --username "$USERNAME" \
  --message-action SUPPRESS \
  --region "$AWS_REGION"

echo "Setting permanent password ..."
aws cognito-idp admin-set-user-password \
  --user-pool-id "$POOL_ID" \
  --username "$USERNAME" \
  --password "$PASSWORD" \
  --permanent \
  --region "$AWS_REGION"

echo ""
echo "Done. Now add these two GitHub Secrets to your repo:"
echo "  SMOKE_TEST_USERNAME = $USERNAME"
echo "  SMOKE_TEST_PASSWORD = (the password you set)"
