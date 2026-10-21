variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "service_name" { type = string }
variable "github_repository" { type = string }
variable "google_search_engine_id" {
  description = "Engine ID for Google Custom Search"
  type        = string
  sensitive   = true
}

variable "pontia_connect_sheet_id" {
  description = "ID of the Google Sheet containing attendee data"
  type        = string
}