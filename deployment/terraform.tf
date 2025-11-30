resource "google_cloud_run_service" "backend" {
  name     = "password-tracker-backend"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "gcr.io/${var.gcp_project_id}/password-tracker-backend:latest"
        
        env {
          name  = "MONGO_URI"
          value = var.mongo_uri
        }
        
        env {
          name  = "FLASK_ENV"
          value = "production"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_container_registry.registry]
}

resource "google_cloud_run_service" "frontend" {
  name     = "password-tracker-frontend"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = "gcr.io/${var.gcp_project_id}/password-tracker-frontend:latest"
        
        env {
          name  = "REACT_APP_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_container_registry.registry]
}

resource "google_container_registry" "registry" {
  project = var.gcp_project_id
}
