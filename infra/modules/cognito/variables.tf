variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "callback_urls" {
  description = "Allowed callback URLs after authentication (CloudFront + localhost)"
  type        = list(string)
}

variable "logout_urls" {
  description = "Allowed logout redirect URLs"
  type        = list(string)
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}
