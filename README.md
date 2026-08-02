# AEOS - AI Education Operations System

## Mission

AEOS is an AI-powered education operations platform designed to improve:

- Teacher productivity
- Student learning outcomes
- Parent engagement
- Assessment intelligence
- Special education workflows

## Core Systems

### 1. AI Assessment Engine
- Diagnostic assessments
- Rubric generation
- Standards alignment
- Feedback generation

### 2. Learning Intelligence Layer
- Student profiles
- Learning pathways
- Intervention recommendations

### 3. Education Operations Dashboard
- Teacher analytics
- Parent communication
- Progress monitoring

## Technology Stack

Frontend:
- React / Next.js

Backend:
- FastAPI

Database:
- PostgreSQL + pgvector

AI:
- Claude API
- RAG pipelines
- AI agents

## Development Status

Current Phase:
MVP Development

Priority:
Pilot → Validation → Revenue

## Environment and Deployment Notes

### Secret handling
- Keep all sensitive values in local environment files and GitHub Codespaces secrets.
- Do not commit Supabase URL, anon key, service-role key, or other credentials to the repository.
- The repository already ignores local environment files through .gitignore.

### Local development template
- Copy backend/.env.example to backend/.env and replace the placeholder values with your own local settings.
- The backend reads the Supabase configuration from backend/.env during development.

### Connection flow
- Codespaces: store secrets in the Codespaces environment or GitHub repository secrets, then expose them as environment variables in the dev container.
- GitHub: use repository or organization secrets for CI/CD and deployment workflows.
- Vercel: set the same environment variables in Vercel project settings for frontend/backend deployments.
- Supabase: use the project URL and service role or anon keys from the Supabase project settings. Keep service-role keys only in server-side environments.

### Recommended setup
1. Create a Supabase project and copy its URL and keys.
2. Create a backend/.env file from backend/.env.example.
3. Add the same values to GitHub or Codespaces secrets if you want CI/CD or remote development to access them.
4. Configure Vercel environment variables to match the production values used by the deployed app.

