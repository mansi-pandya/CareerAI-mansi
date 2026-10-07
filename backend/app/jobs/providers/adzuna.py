"""
Adzuna API job provider.
Docs: https://developer.adzuna.com/docs/search
"""
from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import List, Optional

import httpx

from app.jobs.providers.base import JobProvider, JobData
from app.models.jobs import JobTypeEnum, WorkModeEnum

logger = logging.getLogger(__name__)

# Map Adzuna category/contract_type to our enums
_CONTRACT_MAP = {
    "permanent": JobTypeEnum.full_time,
    "contract": JobTypeEnum.contract,
    "part_time": JobTypeEnum.part_time,
    "temporary": JobTypeEnum.contract,
}

_ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"


def _infer_work_mode(title: str, description: str) -> Optional[WorkModeEnum]:
    combined = f"{title} {description}".lower()
    if "remote" in combined:
        return WorkModeEnum.remote
    if "hybrid" in combined:
        return WorkModeEnum.hybrid
    if "on-site" in combined or "onsite" in combined or "on site" in combined:
        return WorkModeEnum.on_site
    return None


def _parse_salary(job: dict) -> tuple[Optional[int], Optional[int]]:
    sal_min = job.get("salary_min")
    sal_max = job.get("salary_max")
    try:
        return (int(sal_min) if sal_min else None, int(sal_max) if sal_max else None)
    except (ValueError, TypeError):
        return None, None


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


class AdzunaProvider(JobProvider):
    """Fetches jobs from the Adzuna REST API."""

    slug = "adzuna"

    def __init__(self):
        self._app_id = os.environ.get("ADZUNA_APP_ID", "")
        self._api_key = os.environ.get("ADZUNA_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self._app_id and self._api_key)

    def fetch_jobs(
        self,
        keywords: str = "",
        location: str = "",
        job_type: Optional[str] = None,
        work_mode: Optional[str] = None,
        limit: int = 20,
    ) -> List[JobData]:
        if not self.is_available():
            return []

        # Determine country from location or default to 'in' (India)
        country = "in"
        loc_lower = (location or "").lower()
        if any(k in loc_lower for k in ["us", "united states", "usa", "new york", "san francisco"]):
            country = "us"
        elif any(k in loc_lower for k in ["uk", "united kingdom", "london"]):
            country = "gb"
        elif any(k in loc_lower for k in ["canada"]):
            country = "ca"
        elif any(k in loc_lower for k in ["australia"]):
            country = "au"

        params: dict = {
            "app_id": self._app_id,
            "app_key": self._api_key,
            "results_per_page": min(limit, 50),
            "what": keywords or "software developer",
            "content-type": "application/json",
        }
        if location:
            params["where"] = location
        if job_type == "full_time":
            params["full_time"] = 1
        elif job_type == "part_time":
            params["part_time"] = 1

        url = f"{_ADZUNA_BASE}/{country}/search/1"
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.warning("Adzuna API error: %s", exc)
            return []

        results = []
        for item in data.get("results", []):
            sal_min, sal_max = _parse_salary(item)
            contract = item.get("contract_type", "").lower()
            jtype = _CONTRACT_MAP.get(contract)

            loc_display = item.get("location", {}).get("display_name", "")
            loc_area = item.get("location", {}).get("area", [])
            city = loc_area[-1] if loc_area else ""
            country_name = loc_area[0] if loc_area else ""

            desc = item.get("description", "")
            detected_mode = _infer_work_mode(item.get("title", ""), desc)

            jd = JobData(
                external_id=str(item.get("id", "")),
                title=item.get("title", ""),
                company=item.get("company", {}).get("display_name", "Unknown"),
                location=loc_display,
                city=city,
                country=country_name,
                job_type=jtype,
                work_mode=detected_mode,
                salary_min=sal_min,
                salary_max=sal_max,
                salary_currency="GBP" if country == "gb" else ("USD" if country in ("us", "ca", "au") else "INR"),
                description=desc,
                application_url=item.get("redirect_url", ""),
                source_url=item.get("redirect_url", ""),
                posted_date=_parse_date(item.get("created")),
                required_skills=[],
                is_demo=False,
                source_slug="adzuna",
            )
            results.append(jd)

        return results

    def get_job_detail(self, job_id: str) -> Optional[JobData]:
        # Adzuna doesn't have a single-job endpoint; return None
        return None
