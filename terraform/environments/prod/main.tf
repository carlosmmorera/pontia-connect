terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  billing_project = var.project_id
  user_project_override = true
}

module "genai_app" {
  source       = "../../modules/genai_service"
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  service_name = var.service_name
  github_repository = var.github_repository
  pontia_connect_sheet_id = var.pontia_connect_sheet_id
  google_search_engine_id = var.google_search_engine_id
}