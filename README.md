# CareerAI

> Full-stack AI-powered career readiness platform for students.

CareerAI provides career recommendations, skill-gap analysis, interview preparation, resume and ATS analysis, job discovery, and opportunity tracking.

## Local development

```bash
docker compose up --build
```

Open the application at http://localhost:5173. The backend API documentation is available at http://localhost:8000/api/docs when DEBUG is enabled.

## Production deployment

1. Copy the environment templates:

```bash
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

2. Set a strong `SECRET_KEY` and production values in `backend/.env`.
3. Build and start the production stack:

```bash
docker compose up --build -d
```

4. Verify the stack:

```bash
docker compose ps
docker compose logs --tail=100 backend frontend
```

The frontend is served by nginx and supports deep links through SPA fallback routing. API requests are routed to the backend container through `/api`.

## Deployment platforms

The repository includes Docker-compatible deployment files. Host the Docker Compose stack on any provider that supports Docker containers, such as Render, Railway, DigitalOcean App Platform, or a VPS.

For a managed deployment, set the production environment variables in the platform UI and publish the backend and frontend services from this repository. A public hosted URL cannot be generated from the local workspace without the provider account and deployment credentials.
