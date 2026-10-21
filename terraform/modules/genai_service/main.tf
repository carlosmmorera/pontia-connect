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

resource "google_apikeys_key" "search_api_key" {
  name         = "search-api-key-${var.environment}"
  display_name = "Custom Search API Key for ${var.environment}"
  project      = var.project_id

  restrictions {
    api_targets {
      service = "customsearch.googleapis.com"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Secret Manager for sensitive API Keys
resource "google_secret_manager_secret" "search_api_key" {
  secret_id = "GOOGLE_SEARCH_API_KEY_${var.environment}"
  project   = var.project_id
  replication { 
    auto {} 
  }
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "search_api_key_version" {
  secret      = google_secret_manager_secret.search_api_key.id
  secret_data = google_apikeys_key.search_api_key.key_string
}

resource "google_secret_manager_secret" "search_engine_id" {
  secret_id = "GOOGLE_SEARCH_ENGINE_ID_${var.environment}"
  project   = var.project_id
  replication { 
    auto {} 
  }
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "search_engine_id_version" {
  secret      = google_secret_manager_secret.search_engine_id.id
  secret_data = var.google_search_engine_id
}

# Grant Cloud Run SA access to read secrets
resource "google_secret_manager_secret_iam_member" "secret_accessor_key" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.search_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "secret_accessor_engine" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.search_engine_id.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_sa.email}"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "default" {
  name     = "${var.service_name}-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.vertex_ai_user,
    google_secret_manager_secret_version.search_api_key_version,
    google_secret_manager_secret_version.search_engine_id_version
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

      # Secure Secrets Injection
      env {
        name = "GOOGLE_SEARCH_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.search_api_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "GOOGLE_SEARCH_ENGINE_ID"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.search_engine_id.secret_id
            version = "latest"
          }
        }
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