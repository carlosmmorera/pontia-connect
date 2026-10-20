# Outputs for GitHub Secrets

output "github_actions_service_account_email" {
  description = "The email of the Service Account to be stored as a GitHub Secret."
  value       = google_service_account.github_actions_sa.email
}

output "workload_identity_provider_id" {
  description = "The Workload Identity Provider ID to be stored as a GitHub Secret."
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}