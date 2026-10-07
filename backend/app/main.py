from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.database.database import engine, Base, SessionLocal
from app.auth.router import router as auth_router
from app.api.profile import router as profile_router
from app.api.dashboard import router as dashboard_router
from app.api.resume import router as resume_router
from app.api.ats import router as ats_router
from app.api.career import router as career_router
from app.api.jobs import router as jobs_router
from app.api.opportunities import router as opportunities_router
from app.api.interviews import router as interviews_router
from app.api.admin import router as admin_router


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    # Seed career data if not already seeded
    from app.career.seed_data import run_seed
    from app.jobs.seed import seed_job_sources
    db = SessionLocal()
    try:
        run_seed(db)
        seed_job_sources(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered career readiness platform for students",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])
app.include_router(ats_router, prefix="/api/ats", tags=["ATS"])
app.include_router(career_router, prefix="/api/career", tags=["Career"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(opportunities_router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(interviews_router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
