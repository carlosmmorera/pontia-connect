# Dedicated Service Account for the Cloud Run service
resource "google_service_account" "cloudrun_sa" {
  account_id   = "${var.service_name}-sa-${var.environment}"
  display_name = "Cloud Run Service Account for ${var.service_name}"

  depends_on = [google_project_service.required_apis]
}

# Grant Vertex AI User role to the new Service Account
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Artifact Registry Repository
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.service_name}-repo-${var.environment}"
  description   = "Docker repository for ${var.service_name}"
  format        = "DOCKER"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "default" {
  name     = "${var.service_name}-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.vertex_ai_user
  ]

  template {
    service_account = google_service_account.cloudrun_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"

      # Inject environment variables professionally
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "True"
      }
      env {
        name  = "PONTIA_CONNECT_SHEET_ID"
        value = var.pontia_connect_sheet_id 
      }

      ports {
        container_port = 8080
      }
      resources {
        limits = {
          cpu    = "1000m"
          memory = "2048Mi"
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Make the service public
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.default.location
  project  = google_cloud_run_v2_service.default.project
  name     = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}