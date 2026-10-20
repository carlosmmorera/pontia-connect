variable "project_id" {
  type        = string
  description = "ID del proyecto en GCP"
}

variable "region" {
  type        = string
  description = "Región donde se crearán los recursos"
}

variable "environment" {
  type        = string
  description = "Nombre del entorno (ej. pro, dev)"
}

variable "service_name" {
  type        = string
  description = "Nombre del servicio"
}

variable "github_repository" {
  type        = string
  description = "The GitHub repository in the format 'username/repo-name' allowed to deploy."
  # Example: default = "tu-usuario/pontia-connect"
}