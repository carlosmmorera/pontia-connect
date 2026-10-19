# Repositorio de Docker
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.service_name}-repo-${var.environment}"
  description   = "Docker repository for ${var.service_name}"
  format        = "DOCKER"
}

# Servicio de Cloud Run
resource "google_cloud_run_v2_service" "default" {
  name     = "${var.service_name}-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
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

  # Ignorar cambios en la imagen hechos fuera de Terraform (por el pipeline CD)
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Hacer el servicio público para la presentación
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.default.location
  project  = google_cloud_run_v2_service.default.project
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}