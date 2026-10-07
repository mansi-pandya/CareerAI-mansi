"""
Seed job sources (Adzuna + Demo) into the database.
Called on startup if the job_sources table is empty.
"""
from __future__ import annotations

import os
from sqlalchemy.orm import Session

from app.models.jobs import JobSource


_SOURCES = [
    {
        "name": "Adzuna",
        "slug": "adzuna",
        "description": "Real job listings from Adzuna job search API.",
        "api_key_env_var": "ADZUNA_API_KEY",
        "base_url": "https://api.adzuna.com/v1/api/jobs",
        # Active only when API keys are configured
        "is_active_fn": lambda: bool(
            os.environ.get("ADZUNA_APP_ID") and os.environ.get("ADZUNA_API_KEY")
        ),
    },
    {
        "name": "Demo",
        "slug": "demo",
        "description": "Demo job listings for illustration. Not real job postings.",
        "api_key_env_var": None,
        "base_url": None,
        "is_active_fn": lambda: True,
    },
]


def seed_job_sources(db: Session) -> None:
    """Insert job source records if not already present."""
    for src in _SOURCES:
        existing = db.query(JobSource).filter(JobSource.slug == src["slug"]).first()
        if existing:
            # Update is_active based on current env
            existing.is_active = src["is_active_fn"]()
            continue

        js = JobSource(
            name=src["name"],
            slug=src["slug"],
            description=src["description"],
            api_key_env_var=src["api_key_env_var"],
            base_url=src["base_url"],
            is_active=src["is_active_fn"](),
        )
        db.add(js)

    db.commit()
    print("[seed] Job sources seeded.")
