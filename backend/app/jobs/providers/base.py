"""
Abstract base class for job data providers.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from app.models.jobs import JobTypeEnum, WorkModeEnum


@dataclass
class JobData:
    """Normalized job record returned by any provider."""
    title: str
    company: str
    location: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    job_type: Optional[JobTypeEnum] = None
    work_mode: Optional[WorkModeEnum] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    experience_min_years: Optional[float] = None
    experience_max_years: Optional[float] = None
    required_skills: List[str] = field(default_factory=list)
    description: str = ""
    application_url: str = ""
    source_url: str = ""
    external_id: str = ""
    posted_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    is_demo: bool = False
    source_slug: str = ""


class JobProvider(ABC):
    """Base class that all job providers must implement."""

    @property
    @abstractmethod
    def slug(self) -> str:
        """Unique identifier for this provider (e.g. 'adzuna', 'demo')."""

    @abstractmethod
    def fetch_jobs(
        self,
        keywords: str = "",
        location: str = "",
        job_type: Optional[str] = None,
        work_mode: Optional[str] = None,
        limit: int = 20,
    ) -> List[JobData]:
        """Fetch jobs matching the given parameters."""

    @abstractmethod
    def get_job_detail(self, job_id: str) -> Optional[JobData]:
        """Fetch a single job by its external ID."""

    def is_available(self) -> bool:
        """Return True if this provider is properly configured and ready."""
        return True
