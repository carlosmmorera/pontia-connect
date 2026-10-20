# Pontia Connect

An educational and interactive web interface designed to demystify the inner workings of Generative AI models. Explore and visualize core concepts such as tokenization, token probabilities (logprobs), embeddings, and agentic behaviors using the modern Google GenAI SDK and Vertex AI.

## Features

- **Token Prediction Visualization:** Real-time generation of tokens with their corresponding probability distribution.
- **Enterprise-Grade AI:** Powered by Google Cloud's Vertex AI (`gemini-2.5-flash`).
- **Modern Python Stack:** Built with Python 3.12 and ultra-fast dependency management using [`uv`](https://github.com/astral-sh/uv).
- **Secure by Design:** Zero-Trust architecture. No long-lived service account JSON keys are used locally or in CI/CD.
- **Infrastructure as Code (IaC):** Fully reproducible GCP environments using Terraform.

## Architecture

- **App:** Python 3.12 (managed via `uv`), NiceGUI/FastAPI, Google GenAI SDK.
- **Local Environment:** Docker & Docker Compose with Application Default Credentials (ADC) projection.
- **Cloud Infrastructure:** GCP Cloud Run, Artifact Registry, Vertex AI, managed via Terraform.
- **CI/CD:** GitHub Actions with Workload Identity Federation (Keyless authentication).

## Local Development Guide

We use Docker Compose to ensure a seamless and reproducible local development experience across all operating systems, closely mirroring our production environment without compromising security.

### Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine.
2. Install the [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install).
3. Ensure you have access to a Google Cloud Project with the **Vertex AI API** enabled.

### Step-by-Step Setup

**1. Authenticate with Google Cloud**  
Run the following command to log in and generate your Application Default Credentials (ADC). This allows the Docker container to securely impersonate you without downloading vulnerable JSON keys.
```bash
gcloud auth application-default login
```

**2. Configure Environment Variables** 
Copy the template to create your local environment file:
```bash
cp .env.example .env
```

Open the `.env` file and set your variables. Crucially, uncomment the `LOCAL_GCP_CREDS_PATH` **that matches your Operating System** so Docker can mount your ADC credentials:

```
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=europe-west1

# --- LOCAL DEVELOPMENT ONLY ---
# Uncomment the line corresponding to your OS:

# Mac/Linux:
# LOCAL_GCP_CREDS_PATH=~/.config/gcloud/application_default_credentials.json

# Windows (Replace <YourUsername> with your actual Windows user folder):
# LOCAL_GCP_CREDS_PATH=C:/Users/<YourUsername>/AppData/Roaming/gcloud/application_default_credentials.json
```

**3. Build and Run**
Start the application using Docker Compose:
```bash
docker compose up --build
```

The application will be available at `http://localhost:8080`.

## Infrastructure & Deployment

### Terraform (IaC)

The underlying infrastructure is defined in the terraform/ directory. It provisions:

- A dedicated Service Account for Cloud Run (Least Privilege principle).
- Artifact Registry for Docker images.
- Cloud Run service definition.
- IAM bindings for Vertex AI execution.
- Workload Identity Federation (WIF) pools and providers for GitHub Actions.

To provision or update the infrastructure:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Continuous Deployment (CI/CD)

This project uses GitHub Actions (`.github/workflows/cd.yml`) to automatically test, build, and deploy to Cloud Run on every push to the `main` branch.

For security, it uses Workload Identity Federation, meaning GitHub authenticates directly with Google Cloud using short-lived OIDC tokens. No static secrets or service account keys are stored in GitHub.