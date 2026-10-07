"""
Market skill demand analysis.
Analyzes the jobs database to surface in-demand skills
and compare them against a student's current skill set.
"""
from __future__ import annotations

from collections import Counter
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.jobs import Job, JobSource


def get_skill_demand(
    db: Session,
    user_skills: Optional[List[str]] = None,
    top_n: int = 20,
) -> Dict[str, Any]:
    """
    Compute skill demand from the job database.
    Returns top_n skills by frequency with demand_percentage,
    and compares with user_skills if provided.
    """
    jobs = db.query(Job).filter(Job.is_active == True).all()
    total_jobs = len(jobs)
    if total_jobs == 0:
        return {
            "total_jobs_analyzed": 0,
            "top_skills": [],
            "my_skills_in_demand": [],
            "missing_high_demand_skills": [],
        }

    counter: Counter = Counter()
    for job in jobs:
        skills = job.required_skills or []
        for skill in skills:
            counter[skill.strip()] += 1

    # Build top skills list
    top_skills_raw = counter.most_common(top_n)
    top_skills = [
        {
            "skill": skill,
            "count": count,
            "demand_percentage": round(count / total_jobs * 100, 1),
        }
        for skill, count in top_skills_raw
    ]

    # Compare with user skills
    my_skills_in_demand: List[str] = []
    missing_high_demand: List[str] = []

    if user_skills:
        user_skill_names_lower = {s.lower() for s in user_skills}
        for item in top_skills:
            skill_lower = item["skill"].lower()
            matched = any(
                skill_lower in us or us in skill_lower
                for us in user_skill_names_lower
            )
            item["have_skill"] = matched
            if matched:
                my_skills_in_demand.append(item["skill"])
            elif item["demand_percentage"] >= 15.0:
                missing_high_demand.append(item["skill"])
    else:
        for item in top_skills:
            item["have_skill"] = False

    return {
        "total_jobs_analyzed": total_jobs,
        "top_skills": top_skills,
        "my_skills_in_demand": my_skills_in_demand,
        "missing_high_demand_skills": missing_high_demand,
    }


def get_market_trends(db: Session) -> Dict[str, Any]:
    """
    Compute job type and work mode trends, plus top hiring companies.
    """
    jobs = db.query(Job).filter(Job.is_active == True).all()
    total_jobs = len(jobs)

    job_type_counter: Counter = Counter()
    work_mode_counter: Counter = Counter()
    company_counter: Counter = Counter()

    for job in jobs:
        if job.job_type:
            job_type_counter[job.job_type.value] += 1
        if job.work_mode:
            work_mode_counter[job.work_mode.value] += 1
        if job.company:
            company_counter[job.company] += 1

    def _to_trend_list(counter: Counter) -> List[Dict]:
        total = sum(counter.values()) or 1
        return [
            {
                "label": k.replace("_", " ").title(),
                "count": v,
                "percentage": round(v / total * 100, 1),
            }
            for k, v in counter.most_common()
        ]

    top_companies = [
        {"company": name, "job_count": count}
        for name, count in company_counter.most_common(10)
    ]

    return {
        "total_jobs": total_jobs,
        "job_type_trends": _to_trend_list(job_type_counter),
        "work_mode_trends": _to_trend_list(work_mode_counter),
        "top_companies": top_companies,
    }
