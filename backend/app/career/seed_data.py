"""
Seed function: populate Career and LearningResource tables from in-memory profiles.
Called on startup if the careers table is empty.
"""
from __future__ import annotations

import re
from sqlalchemy.orm import Session

from app.models.career import Career, LearningResource
from app.career.recommender import CAREER_PROFILES
from app.career.learning import RESOURCES


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def seed_careers(db: Session) -> None:
    """Insert all 15 career profiles if the careers table is empty."""
    existing = db.query(Career).count()
    if existing > 0:
        return

    for slug, data in CAREER_PROFILES.items():
        career = Career(
            name=data["name"],
            slug=slug,
            description=data.get("description", ""),
            industry=data.get("industry", ""),
            required_skills=data.get("required_skills", []),
            preferred_skills=data.get("preferred_skills", []),
            education_requirements={
                "degrees": ["Bachelor", "Master", "PhD"],
                "fields": data.get("education_fields", []),
            },
            market_demand_score=data.get("market_demand_score", 0.0),
            avg_salary_min=data.get("avg_salary_min", 0),
            avg_salary_max=data.get("avg_salary_max", 0),
            growth_rate=data.get("growth_rate", 0.0),
        )
        db.add(career)

    db.commit()
    print(f"[seed] Inserted {len(CAREER_PROFILES)} career profiles.")


def seed_learning_resources(db: Session) -> None:
    """Insert all curated learning resources if the table is empty."""
    existing = db.query(LearningResource).count()
    if existing > 0:
        return

    for r in RESOURCES:
        resource = LearningResource(
            skill_name=r["skill_name"],
            resource_name=r["resource_name"],
            provider=r["provider"],
            url=r["url"],
            topics=r.get("topics", []),
            difficulty=r.get("difficulty", "beginner"),
            is_free=r.get("is_free", True),
            duration_hours=r.get("duration_hours", 0.0),
            description=r.get("description", ""),
            why_recommended=r.get("why_recommended", ""),
        )
        db.add(resource)

    db.commit()
    print(f"[seed] Inserted {len(RESOURCES)} learning resources.")


def run_seed(db: Session) -> None:
    """Run all seed functions."""
    seed_careers(db)
    seed_learning_resources(db)
