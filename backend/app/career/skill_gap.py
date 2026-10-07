"""
Skill gap analyzer.

Given a student's skills and a target career, produces:
  - matched_skills  – skills the student already has (with level info)
  - missing_skills  – skills the student lacks (with importance / priority)
  - summary metrics
"""
from __future__ import annotations

from typing import List, Dict, Any

from app.career.recommender import CAREER_PROFILES


_PROF_TO_LEVEL = {
    "beginner": 1,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}

# Required skills get higher importance weights than preferred
_REQUIRED_IMPORTANCE = "critical"
_PREFERRED_IMPORTANCE = "important"


def _priority(importance: str, gap: int) -> str:
    """Derive priority label from importance + gap size."""
    if importance == "critical" and gap >= 2:
        return "high"
    if importance == "critical" and gap == 1:
        return "high"
    if importance == "important" and gap >= 2:
        return "medium"
    if importance == "important" and gap == 1:
        return "medium"
    return "low"


def analyze_skill_gap(
    career_slug: str,
    student_skills: List[Dict[str, Any]],  # [{name, proficiency}, ...]
) -> Dict[str, Any]:
    """
    Returns a structured skill-gap report.

    matched_skills entries:
        {skill_name, current_level, required_level, proficiency}

    missing_skills entries:
        {skill_name, importance, current_level, required_level, gap, priority}
    """
    profile = CAREER_PROFILES.get(career_slug)
    if not profile:
        return {"error": f"Unknown career slug: {career_slug}"}

    required_skills = [s.lower() for s in profile["required_skills"]]
    preferred_skills = [s.lower() for s in profile["preferred_skills"]]

    student_map: Dict[str, int] = {
        s["name"].lower(): _PROF_TO_LEVEL.get(s.get("proficiency", "beginner"), 1)
        for s in student_skills
    }
    student_names = set(student_map.keys())

    matched: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []

    # Required skills – level 3 required by default
    for skill in required_skills:
        required_level = 3
        if skill in student_names:
            current = student_map[skill]
            gap = max(required_level - current, 0)
            matched.append({
                "skill_name": skill,
                "importance": _REQUIRED_IMPORTANCE,
                "current_level": current,
                "required_level": required_level,
                "gap": gap,
                "proficiency": _level_to_prof(current),
            })
        else:
            missing.append({
                "skill_name": skill,
                "importance": _REQUIRED_IMPORTANCE,
                "current_level": 0,
                "required_level": required_level,
                "gap": required_level,
                "priority": _priority(_REQUIRED_IMPORTANCE, required_level),
            })

    # Preferred skills – level 2 required
    for skill in preferred_skills:
        if skill in required_skills:
            continue  # already handled
        required_level = 2
        if skill in student_names:
            current = student_map[skill]
            gap = max(required_level - current, 0)
            matched.append({
                "skill_name": skill,
                "importance": _PREFERRED_IMPORTANCE,
                "current_level": current,
                "required_level": required_level,
                "gap": gap,
                "proficiency": _level_to_prof(current),
            })
        else:
            missing.append({
                "skill_name": skill,
                "importance": _PREFERRED_IMPORTANCE,
                "current_level": 0,
                "required_level": required_level,
                "gap": required_level,
                "priority": _priority(_PREFERRED_IMPORTANCE, required_level),
            })

    # Sort missing by priority (high first), then importance
    priority_order = {"high": 0, "medium": 1, "low": 2}
    importance_order = {"critical": 0, "important": 1, "nice-to-have": 2}
    missing.sort(key=lambda x: (priority_order[x["priority"]], importance_order[x["importance"]]))

    total = len(required_skills) + len(preferred_skills)
    match_pct = round(len(matched) / max(total, 1) * 100, 1)

    return {
        "career_name": profile["name"],
        "career_slug": career_slug,
        "total_required": total,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "match_percentage": match_pct,
        "matched_skills": matched,
        "missing_skills": missing,
    }


def _level_to_prof(level: int) -> str:
    if level >= 5:
        return "expert"
    if level >= 4:
        return "advanced"
    if level >= 2:
        return "intermediate"
    return "beginner"


def simulate_skill_addition(
    career_slug: str,
    current_skills: List[Dict[str, Any]],
    new_skill_names: List[str],
    current_match: float,
) -> Dict[str, Any]:
    """
    Estimate the new match score if the student learns `new_skill_names`.
    Returns current vs estimated match with explanation.
    """
    profile = CAREER_PROFILES.get(career_slug)
    if not profile:
        return {"error": f"Unknown career slug: {career_slug}"}

    # Add new skills at intermediate level
    augmented = list(current_skills)
    added: List[str] = []
    existing_names = {s["name"].lower() for s in current_skills}
    for skill in new_skill_names:
        if skill.lower() not in existing_names:
            augmented.append({"name": skill.lower(), "proficiency": "intermediate"})
            added.append(skill)

    if not added:
        return {
            "career_name": profile["name"],
            "career_slug": career_slug,
            "current_match": current_match,
            "estimated_match": current_match,
            "skills_added": [],
            "improvement": 0.0,
            "explanation": "You already have all selected skills.",
        }

    # Re-analyse gap with augmented skill set
    current_gap = analyze_skill_gap(career_slug, current_skills)
    new_gap = analyze_skill_gap(career_slug, augmented)

    improvement = new_gap["match_percentage"] - current_gap["match_percentage"]
    estimated = min(current_match + improvement * 0.4, 100.0)  # skill score is 40% of composite

    required_skills = [s.lower() for s in profile["required_skills"]]
    critical_added = [s for s in added if s.lower() in required_skills]

    if critical_added:
        explanation = (
            f"Learning {', '.join(critical_added)} would directly address required skills "
            f"for {profile['name']}, boosting your match by ~{improvement:.1f}%."
        )
    else:
        explanation = (
            f"Learning {', '.join(added)} would improve your preferred skill coverage "
            f"for {profile['name']} by ~{improvement:.1f}%."
        )

    return {
        "career_name": profile["name"],
        "career_slug": career_slug,
        "current_match": round(current_match, 1),
        "estimated_match": round(estimated, 1),
        "skills_added": added,
        "improvement": round(improvement * 0.4, 1),
        "explanation": explanation,
    }
