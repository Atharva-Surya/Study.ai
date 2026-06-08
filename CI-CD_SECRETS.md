CI/CD Secrets and Setup

Required repository secrets (set in GitHub Settings → Secrets & variables → Actions):

- `VERCEL_TOKEN` — Personal token from Vercel used by the action.
- `VERCEL_ORG_ID` — Your Vercel organization ID.
- `VERCEL_PROJECT_ID_PRODUCTION` — Vercel project ID for the production site.
- `VERCEL_PROJECT_ID_STAGING` — Vercel project ID for the staging site (optional).
- `RENDER_API_KEY` — API key for Render to trigger deploys.
- `RENDER_SERVICE_ID_PRODUCTION` — Render service ID for production deploys.
- `RENDER_SERVICE_ID_STAGING` — Render service ID for staging deploys.

Optional / recommended:
- Configure GitHub `environments` (e.g., `production`) and add required reviewers for production deploy jobs.
- If you use Vercel / Render's native GitHub integrations, you can omit the deploy steps in workflows and rely on their automatic preview/prod deploys.

How the pipeline works:
- PRs: run lint, tests, and build (no automatic production deploy).
- `develop` branch: run build/tests and deploy to staging (Vercel staging project and Render staging service).
- `main` branch: run build/tests and deploy to production (Vercel production project and Render production service).
