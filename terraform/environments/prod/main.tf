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
}

module "genai_app" {
  source       = "../../modules/genai_service"
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  service_name = var.service_name
}