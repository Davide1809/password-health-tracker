# Deployment Attempt Notes

This file documents the manual deployment attempts performed during Sprint 1 and the current status.

Date: November 30, 2025  
Status: **✅ DEPLOYMENT SUCCESSFUL**

## Goal
Attempt to deploy the Password Health Tracker application to Google Cloud (Cloud Run / GCR) as a manual proof-of-concept.

## What was accomplished
1. ✅ Created GCP project: `password-health-tracker-final`
2. ✅ Created service account `gh-actions-deployer` with necessary IAM roles
3. ✅ Generated and securely stored service account key (JSON)
4. ✅ Added GitHub Actions secrets (`GCP_PROJECT`, `GCP_SA_KEY_JSON`)
5. ✅ Updated GitHub Actions workflow with proper GCP auth and deployment
6. ✅ Fixed container port compatibility (PORT=8080 for Cloud Run)
7. ✅ Built and pushed Docker images to GCR (amd64 architecture)
8. ✅ Deployed both services to Cloud Run successfully

## Deployed Services

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | https://password-tracker-backend-772dxjzyra-uc.a.run.app | ✅ Running |
| **Frontend** | https://password-tracker-frontend-772dxjzyra-uc.a.run.app | ✅ Running |

## What worked
- GitHub `gh` CLI integration for secrets management
- GCP service account creation and IAM role assignment
- Cloud Run deployment with health checks and port configuration
- Docker multi-architecture builds with `docker buildx`

## Issues resolved
1. **Multi-arch Docker images**: Used `docker buildx` with `--platform linux/amd64`
2. **Port misconfiguration**: Updated Flask and nginx to listen on PORT=8080
3. **Startup timeout**: Added `/health` endpoint for nginx readiness probes
4. **GCP billing**: Enabled billing to activate Cloud Run and Build APIs

## Next steps
1. ✅ Create GCP project — DONE
2. ✅ Create service account — DONE
3. ✅ Add GitHub secrets — DONE
4. ⏳ Merge PR #1 to main
5. ⏳ Enable automatic CI/CD deployments
6. ⏳ Connect frontend to backend Cloud Run URL
7. ⏳ Set up MongoDB Atlas for persistent data
8. ⏳ Add custom domain and HTTPS

## GitHub Actions Workflow
CI/CD pipeline ready:
- **Trigger**: Push to `main`
- **Steps**: Test → Build → Push → Deploy to Cloud Run

To enable: Merge PR #1 to `main`

## Helpful commands

```bash
# Deploy manually
gcloud run deploy password-tracker-backend \
  --image=gcr.io/password-health-tracker-final/password-tracker-backend:latest \
  --platform=managed --region=us-central1 --allow-unauthenticated \
  --project=password-health-tracker-final

# Get URLs
gcloud run services describe password-tracker-backend \
  --region=us-central1 --project=password-health-tracker-final --format='value(status.url)'

# View logs
gcloud run services logs read password-tracker-backend \
  --region=us-central1 --project=password-health-tracker-final --limit=50
```

## Resources
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [GitHub Actions for Google Cloud](https://github.com/google-github-actions)
- [GCP Project Console](https://console.cloud.google.com/run?project=password-health-tracker-final)
