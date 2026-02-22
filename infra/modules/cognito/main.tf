# --- Cognito User Pool ---

resource "aws_cognito_user_pool" "main" {
  name = "${var.project_name}-${var.environment}"

  # Email as sign-in alias
  alias_attributes = ["email"]

  # Auto-verify email
  auto_verified_attributes = ["email"]

  # Password policy — simple for family use
  password_policy {
    minimum_length    = 8
    require_lowercase = false
    require_numbers   = false
    require_symbols   = false
    require_uppercase = false
  }

  # Account recovery via email only (no SMS — free)
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# --- Cognito-hosted Domain (free) ---

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-auth-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id
}

# --- Google Identity Provider ---

resource "aws_cognito_identity_provider" "google" {
  user_pool_id  = aws_cognito_user_pool.main.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    client_id                     = var.google_client_id
    client_secret                 = var.google_client_secret
    authorize_scopes              = "openid email profile"
    authorize_url                 = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url                     = "https://www.googleapis.com/oauth2/v4/token"
    token_request_method          = "POST"
    oidc_issuer                   = "https://accounts.google.com"
    attributes_url                = "https://people.googleapis.com/v1/people/me?personFields="
    attributes_url_add_attributes = "true"
  }

  attribute_mapping = {
    email    = "email"
    name     = "name"
    username = "sub"
  }
}

# --- User Pool Client (public SPA — no client secret) ---

resource "aws_cognito_user_pool_client" "frontend" {
  name         = "${var.project_name}-frontend-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id

  # Supported identity providers
  supported_identity_providers = ["COGNITO", "Google"]

  # OAuth configuration
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email", "profile"]

  # Redirect URLs
  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  # No client secret — public SPA client
  generate_secret = false

  # Token validity
  access_token_validity  = 1  # 1 hour
  refresh_token_validity = 30 # 30 days

  token_validity_units {
    access_token  = "hours"
    refresh_token = "days"
  }

  # Wait for Google provider to be created first
  depends_on = [aws_cognito_identity_provider.google]
}

# --- Resource Server (defines scopes for machine-to-machine clients) ---

resource "aws_cognito_resource_server" "api" {
  identifier   = "trip-assistant-api"
  name         = "${var.project_name}-api-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id

  scope {
    scope_name        = "smoke-test"
    scope_description = "CI/CD smoke test access"
  }
}

# --- Machine Client (CI/CD smoke tests — client credentials grant) ---

resource "aws_cognito_user_pool_client" "smoke_test" {
  name         = "${var.project_name}-smoke-test-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id

  # Client credentials flow (machine-to-machine, no user login)
  allowed_oauth_flows                  = ["client_credentials"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["trip-assistant-api/smoke-test"]

  # Generate a secret — required for client_credentials grant
  generate_secret = true

  # Short token validity — smoke tests only need minutes
  access_token_validity = 1 # 1 hour

  token_validity_units {
    access_token = "hours"
  }

  depends_on = [aws_cognito_resource_server.api]
}
