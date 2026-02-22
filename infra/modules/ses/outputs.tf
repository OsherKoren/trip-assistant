output "email_identity_arn" {
  description = "ARN of the SES email identity"
  value       = aws_ses_email_identity.feedback.arn
}
