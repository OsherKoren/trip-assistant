# --- SES Email Identity for Feedback Notifications ---

resource "aws_ses_email_identity" "feedback" {
  email = var.feedback_email
}
