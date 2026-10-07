"""
Apply / Upskill Advisor
Compares extracted opportunity data against a student's profile and skill set
to produce a clear apply recommendation.
"""
import re
from typing import List, Optional, Dict

from app.schemas.opportunities import ExtractedOpportunityData, ApplyRecommendation
from app.models.opportunities import ApplyRecommendationEnum


# ── Curated learning resource links per skill ─────────────────────────────────
_LEARNING_RESOURCES: Dict[str, Dict[str, str]] = {
    "python": {"name": "Python – freeCodeCamp", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
    "javascript": {"name": "JavaScript – MDN", "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript"},
    "typescript": {"name": "TypeScript – Official Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
    "react": {"name": "React – Official Docs", "url": "https://react.dev/learn"},
    "node": {"name": "Node.js – Full Course", "url": "https://nodejs.dev/en/learn/"},
    "nodejs": {"name": "Node.js – Full Course", "url": "https://nodejs.dev/en/learn/"},
    "django": {"name": "Django – Official Tutorial", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/"},
    "flask": {"name": "Flask – Quickstart", "url": "https://flask.palletsprojects.com/en/stable/quickstart/"},
    "fastapi": {"name": "FastAPI – Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
    "sql": {"name": "SQL – W3Schools", "url": "https://www.w3schools.com/sql/"},
    "mysql": {"name": "MySQL – Tutorial", "url": "https://www.mysqltutorial.org/"},
    "postgresql": {"name": "PostgreSQL – Tutorial", "url": "https://www.postgresqltutorial.com/"},
    "mongodb": {"name": "MongoDB – University", "url": "https://university.mongodb.com/"},
    "aws": {"name": "AWS – Free Tier + Training", "url": "https://aws.amazon.com/training/"},
    "azure": {"name": "Azure – Microsoft Learn", "url": "https://learn.microsoft.com/en-us/training/azure/"},
    "gcp": {"name": "GCP – Google Cloud Skills Boost", "url": "https://cloudskillsboost.google/"},
    "docker": {"name": "Docker – Get Started", "url": "https://docs.docker.com/get-started/"},
    "kubernetes": {"name": "Kubernetes – Official Tutorial", "url": "https://kubernetes.io/docs/tutorials/"},
    "git": {"name": "Git – Pro Git Book", "url": "https://git-scm.com/book/en/v2"},
    "machine learning": {"name": "ML – Andrew Ng Coursera", "url": "https://www.coursera.org/learn/machine-learning"},
    "deep learning": {"name": "Deep Learning Specialization – Coursera", "url": "https://www.coursera.org/specializations/deep-learning"},
    "tensorflow": {"name": "TensorFlow – Official Tutorials", "url": "https://www.tensorflow.org/tutorials"},
    "pytorch": {"name": "PyTorch – Tutorials", "url": "https://pytorch.org/tutorials/"},
    "data science": {"name": "Data Science – Kaggle Learn", "url": "https://www.kaggle.com/learn"},
    "data analysis": {"name": "Data Analysis – Kaggle Learn", "url": "https://www.kaggle.com/learn/pandas"},
    "excel": {"name": "Excel – Microsoft Support", "url": "https://support.microsoft.com/en-us/excel"},
    "power bi": {"name": "Power BI – Microsoft Learn", "url": "https://learn.microsoft.com/en-us/power-bi/"},
    "tableau": {"name": "Tableau – Free Training", "url": "https://www.tableau.com/learn/training"},
    "java": {"name": "Java – Oracle Tutorial", "url": "https://dev.java/learn/"},
    "kotlin": {"name": "Kotlin – Official Docs", "url": "https://kotlinlang.org/docs/getting-started.html"},
    "swift": {"name": "Swift – Apple Developer", "url": "https://developer.apple.com/swift/"},
    "flutter": {"name": "Flutter – Get Started", "url": "https://flutter.dev/docs/get-started/codelab"},
    "golang": {"name": "Go – Tour of Go", "url": "https://go.dev/tour/"},
    "rust": {"name": "Rust – The Book", "url": "https://doc.rust-lang.org/book/"},
    "devops": {"name": "DevOps – Roadmap.sh", "url": "https://roadmap.sh/devops"},
    "linux": {"name": "Linux – The Linux Command Line", "url": "https://linuxcommand.org/tlcl.php"},
    "figma": {"name": "Figma – Learn Design", "url": "https://www.figma.com/resources/learn-design/"},
}

_DEFAULT_RESOURCE = {"name": "Search on Coursera", "url": "https://www.coursera.org/search?query={skill}"}


def _normalise_skill(s: str) -> str:
    return re.sub(r"[^a-z0-9 +#]", "", s.lower().strip())


def _skill_match(student_skills: List[str], required_skills: List[str]):
    """
    Return (matched: list, missing: list, match_pct: float).
    Case-insensitive, normalised comparison.
    """
    if not required_skills:
        return [], [], 100.0

    norm_student = {_normalise_skill(s) for s in student_skills}
    norm_required = [_normalise_skill(s) for s in required_skills]

    matched = [r for r in norm_required if r in norm_student]
    missing = [r for r in norm_required if r not in norm_student]
    pct = (len(matched) / len(norm_required)) * 100 if norm_required else 100.0
    return matched, missing, pct


def _experience_match(required_exp: Optional[str], student_years: float) -> bool:
    """
    Return True if student experience meets the requirement.
    Parses patterns like "2 years", "1-3 years", "0-1 years", "fresher".
    """
    if not required_exp:
        return True  # no requirement stated

    low = re.search(r"(\d+(?:\.\d+)?)", required_exp)
    if not low:
        return True
    min_years = float(low.group(1))
    return student_years >= min_years


def _upskill_suggestions(missing_skills: List[str]) -> List[Dict[str, str]]:
    suggestions = []
    for skill in missing_skills[:8]:  # cap at 8 suggestions
        norm = _normalise_skill(skill)
        resource = _LEARNING_RESOURCES.get(norm)
        if resource:
            suggestions.append({"skill": skill, **resource})
        else:
            suggestions.append({
                "skill": skill,
                "name": f"Search \"{skill}\" on Coursera",
                "url": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
            })
    return suggestions


def compare_opportunity_with_profile(
    extracted_data: ExtractedOpportunityData,
    student_profile,        # SQLAlchemy StudentProfile ORM object
    student_skills: List,   # list of StudentSkill ORM objects (with .skill.name)
) -> ApplyRecommendation:
    """
    Compare extracted job requirements against the student's profile/skills
    and return a recommendation.
    """
    # Gather student skill names
    skill_names = []
    student_years = 0.0
    try:
        for ss in student_skills:
            skill_names.append(ss.skill.name)
            student_years = max(student_years, getattr(ss, "years_experience", 0.0) or 0.0)
    except Exception:
        pass

    required_skills = extracted_data.skills_required or []
    matched, missing, match_pct = _skill_match(skill_names, required_skills)
    exp_ok = _experience_match(extracted_data.experience_required, student_years)

    # ── Determine recommendation ──────────────────────────────────────────
    if not required_skills:
        # No skills specified — we can at least encourage
        recommendation = ApplyRecommendationEnum.apply_now
        reasoning = (
            "No specific skill requirements were detected in this listing. "
            "You may apply and highlight your existing skills."
        )
    elif match_pct >= 80 and exp_ok:
        recommendation = ApplyRecommendationEnum.apply_now
        reasoning = (
            f"You match {match_pct:.0f}% of the required skills and your experience level "
            "meets the requirement. This is a strong fit — apply now!"
        )
    elif match_pct >= 50:
        recommendation = ApplyRecommendationEnum.apply_upskill
        if missing:
            gap_str = ", ".join(missing[:4]) + ("..." if len(missing) > 4 else "")
            reasoning = (
                f"You match {match_pct:.0f}% of the required skills. "
                f"You can apply now while simultaneously working on: {gap_str}. "
                "Many employers value candidates who are proactively learning."
            )
        else:
            reasoning = (
                f"You match {match_pct:.0f}% of the skills. "
                "Apply now and mention your ongoing learning in your cover letter."
            )
    elif match_pct >= 30:
        recommendation = ApplyRecommendationEnum.consider_after_upskill
        if missing:
            gap_str = ", ".join(missing[:5]) + ("..." if len(missing) > 5 else "")
            reasoning = (
                f"You currently match {match_pct:.0f}% of the required skills. "
                f"Closing the gap in {gap_str} will significantly improve your chances. "
                "Consider applying after a short focused learning sprint."
            )
        else:
            reasoning = (
                f"You match {match_pct:.0f}% of the skills required. "
                "Upskilling before applying will improve your competitiveness."
            )
    else:
        recommendation = ApplyRecommendationEnum.dont_prioritize
        if missing:
            gap_str = ", ".join(missing[:5]) + ("..." if len(missing) > 5 else "")
            reasoning = (
                f"There is a significant skill gap — you currently match only {match_pct:.0f}% "
                f"of the requirements. Key missing skills: {gap_str}. "
                "Focus on building foundational skills before targeting this type of role."
            )
        else:
            reasoning = (
                f"You match {match_pct:.0f}% of the required skills. "
                "This role is not an immediate priority given the current skill gap."
            )

    return ApplyRecommendation(
        recommendation=recommendation,
        reasoning=reasoning,
        matched_skills=matched,
        missing_skills=missing,
        upskill_suggestions=_upskill_suggestions(missing),
    )
