"""
ATS (Applicant Tracking System) Scoring Analyzer.

Scores a parsed resume across 9 dimensions:
  structure, formatting, keywords, skills, projects,
  experience, education, contact, job_alignment

All scores are 0–100. Weights sum to 1.0.
"""
import re
import math
from typing import Optional

from app.ats.recommendations import generate_recommendations


# ─── Dimension weights ────────────────────────────────────────────────────────

WEIGHTS = {
    "structure": 0.12,
    "formatting": 0.10,
    "keywords": 0.13,
    "skills": 0.12,
    "projects": 0.13,
    "experience": 0.12,
    "education": 0.10,
    "contact": 0.08,
    "job_alignment": 0.10,
}

# ─── Common tech keywords for keyword scoring ─────────────────────────────────

TECH_KEYWORDS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "bash", "perl",
    # Web
    "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
    "spring", "nextjs", "html", "css", "graphql", "rest api", "jquery",
    "tailwind", "bootstrap",
    # DB
    "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "sql",
    "nosql", "dynamodb", "cassandra", "elasticsearch", "firebase",
    # AI/ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "nlp", "computer vision", "data science", "neural network",
    "llm", "transformers", "pandas", "numpy", "matplotlib",
    # Cloud
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "terraform",
    "heroku", "vercel", "serverless",
    # Tools
    "git", "github", "linux", "agile", "scrum", "jira", "postman", "figma",
    # Data
    "tableau", "power bi", "excel", "spark", "hadoop", "data analysis",
    "data visualization",
}

ACTION_VERBS = {
    "developed", "built", "designed", "implemented", "created", "led",
    "managed", "optimized", "improved", "reduced", "increased", "achieved",
    "deployed", "architected", "automated", "integrated", "delivered",
    "collaborated", "mentored", "researched", "analyzed", "engineered",
    "launched", "established", "streamlined", "maintained", "contributed",
    "refactored", "migrated", "scaled", "secured", "tested", "documented",
}


def _flatten_text(data: dict) -> str:
    """Flatten all text fields in parsed data into a single lowercase string."""
    parts = []

    def recurse(obj):
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)
        elif isinstance(obj, dict):
            for v in obj.values():
                recurse(v)

    recurse(data)
    return " ".join(parts).lower()


# ─── Scoring dimensions ───────────────────────────────────────────────────────

def score_contact(contact: dict) -> tuple[float, dict]:
    """Score 0–100 based on presence of contact fields."""
    fields = {
        "name": 20,
        "email": 25,
        "phone": 20,
        "linkedin": 15,
        "github": 15,
        "location": 5,
    }
    score = 0
    present = []
    missing = []
    for field, weight in fields.items():
        val = contact.get(field)
        if val and str(val).strip():
            score += weight
            present.append(field)
        else:
            missing.append(field)

    return min(100.0, float(score)), {"present": present, "missing": missing}


def score_structure(data: dict) -> tuple[float, dict]:
    """Score 0–100 based on presence of key resume sections."""
    sections = {
        "contact": 20,
        "education": 20,
        "skills": 20,
        "projects": 20,  # projects OR experience
        "experience": 0,  # credited via projects
    }
    present = []
    missing = []
    score = 0

    contact = data.get("contact") or {}
    has_contact = any(v for v in contact.values() if v)
    if has_contact:
        score += 20
        present.append("contact")
    else:
        missing.append("contact")

    education = data.get("education") or []
    if education:
        score += 20
        present.append("education")
    else:
        missing.append("education")

    skills = data.get("skills") or {}
    skills_flat = []
    for v in skills.values():
        if isinstance(v, list):
            skills_flat.extend(v)
    if skills_flat:
        score += 20
        present.append("skills")
    else:
        missing.append("skills")

    projects = data.get("projects") or []
    experience = data.get("experience") or []
    if projects or experience:
        score += 20
        present.append("projects_or_experience")
    else:
        missing.append("projects_or_experience")

    # Bonus: certifications or achievements
    certs = data.get("certifications") or []
    achievements = data.get("achievements") or []
    if certs or achievements:
        score += 20
        present.append("extras")
    else:
        missing.append("extras")

    return min(100.0, float(score)), {"present": present, "missing": missing}


def score_formatting(raw_text: str, data: dict) -> tuple[float, dict]:
    """Score 0–100 based on formatting quality."""
    score = 60  # base
    notes = []

    # Length check: a good resume is ~300–1000 words
    word_count = len(raw_text.split()) if raw_text else 0
    if 300 <= word_count <= 1200:
        score += 15
        notes.append(f"Good length ({word_count} words)")
    elif word_count < 100:
        score -= 20
        notes.append(f"Too short ({word_count} words)")
    elif word_count > 2000:
        score -= 10
        notes.append(f"Too long ({word_count} words)")

    # Bullet point usage
    bullet_count = len(re.findall(r"[•\-\*\u2022]", raw_text))
    if bullet_count >= 5:
        score += 15
        notes.append(f"Uses bullet points ({bullet_count})")
    elif bullet_count == 0:
        score -= 15
        notes.append("No bullet points found")

    # Date format consistency
    date_matches = re.findall(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}\b",
        raw_text, re.I
    )
    if date_matches:
        score += 10
        notes.append("Consistent month-year date format")

    return max(0.0, min(100.0, float(score))), {"notes": notes, "word_count": word_count}


def score_keywords(raw_text: str, data: dict) -> tuple[float, dict]:
    """TF-IDF-style keyword scoring against a predefined tech keyword dictionary."""
    if not raw_text:
        return 0.0, {"matched": [], "count": 0}

    text_lower = raw_text.lower()
    matched = []
    for kw in TECH_KEYWORDS:
        if kw in text_lower:
            matched.append(kw)

    # Score: percentage of common keywords present (cap at 30 for 100%)
    count = len(matched)
    score = min(100.0, (count / 30) * 100)

    return score, {"matched": matched, "count": count, "total_keywords": len(TECH_KEYWORDS)}


def score_skills(data: dict) -> tuple[float, dict]:
    """Score 0–100 based on quantity and diversity of skills."""
    skills = data.get("skills") or {}
    total_skills = 0
    categories_with_skills = 0

    for v in skills.values():
        if isinstance(v, list) and v:
            total_skills += len(v)
            categories_with_skills += 1

    # 20+ skills = full score for count
    count_score = min(60.0, (total_skills / 20) * 60)
    # 4+ categories = full diversity score
    diversity_score = min(40.0, (categories_with_skills / 4) * 40)
    score = count_score + diversity_score

    return min(100.0, score), {
        "total_skills": total_skills,
        "categories": categories_with_skills,
    }


def score_projects(data: dict) -> tuple[float, dict]:
    """Score 0–100 based on quality of project descriptions."""
    projects = data.get("projects") or []
    if not projects:
        return 0.0, {"count": 0, "issues": ["No projects found"]}

    score = 0
    issues = []
    base_per_project = min(30, 100 // max(len(projects), 1))
    project_scores = []

    for p in projects[:5]:  # score up to 5 projects
        ps = 0
        if p.get("name"):
            ps += 20
        if p.get("description") and len(str(p.get("description", ""))) > 30:
            ps += 25
        else:
            issues.append(f"Project '{p.get('name', 'Unknown')}' lacks description")
        if p.get("tech_stack") and len(p["tech_stack"]) > 0:
            ps += 25
        else:
            issues.append(f"Project '{p.get('name', 'Unknown')}' missing tech stack")
        if p.get("github_url"):
            ps += 15
        if p.get("results") or p.get("contributions"):
            ps += 15
        project_scores.append(min(100, ps))

    score = sum(project_scores) / max(len(project_scores), 1) if project_scores else 0

    return min(100.0, score), {"count": len(projects), "issues": issues}


def score_experience(data: dict) -> tuple[float, dict]:
    """Score based on action verbs, quantified achievements, and completeness."""
    experience = data.get("experience") or []
    projects = data.get("projects") or []

    # Combine experience + project descriptions for action verb analysis
    all_text = []
    for exp in experience:
        for r in exp.get("responsibilities", []):
            all_text.append(str(r))
        for a in exp.get("achievements", []):
            all_text.append(str(a))
    for proj in projects:
        if proj.get("description"):
            all_text.append(str(proj["description"]))

    if not all_text and not experience:
        return 30.0, {
            "action_verb_count": 0,
            "quantified_count": 0,
            "note": "No experience section; base score from projects",
        }

    combined = " ".join(all_text).lower()

    # Action verbs
    verb_count = sum(1 for v in ACTION_VERBS if v in combined)
    verb_score = min(40.0, (verb_count / 8) * 40)

    # Quantified achievements: numbers with % or K or M or x
    quant_matches = re.findall(r"\d+(?:\.\d+)?(?:\s*%|\s*[kKmM]x?|\s*times?|\s*users?|\s*hours?)", combined)
    quant_score = min(30.0, len(quant_matches) * 10)

    # Has actual experience entries?
    exp_score = min(30.0, len(experience) * 15) if experience else 20.0

    score = verb_score + quant_score + exp_score

    return min(100.0, score), {
        "action_verb_count": verb_count,
        "quantified_count": len(quant_matches),
        "experience_entries": len(experience),
    }


def score_education(data: dict) -> tuple[float, dict]:
    """Score 0–100 based on education completeness."""
    education = data.get("education") or []
    if not education:
        return 30.0, {"count": 0, "issues": ["No education found"]}

    score = 0
    issues = []
    for edu in education[:2]:
        if edu.get("institution"):
            score += 25
        if edu.get("degree") or edu.get("field_of_study"):
            score += 25
        if edu.get("cgpa"):
            score += 25
        else:
            issues.append("CGPA not found")
        if edu.get("start_date") or edu.get("end_date"):
            score += 25
        else:
            issues.append("Education dates missing")

    return min(100.0, float(score)), {"count": len(education), "issues": issues}


# ─── Job alignment scoring ────────────────────────────────────────────────────

def _tokenize(text: str) -> dict:
    """Simple TF vector from text."""
    tokens = re.findall(r"\b\w{3,}\b", text.lower())
    tf: dict = {}
    for tok in tokens:
        tf[tok] = tf.get(tok, 0) + 1
    return tf


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two TF vectors."""
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[k] * vec_b[k] for k in common)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def score_job_alignment(raw_text: str, job_description: Optional[str]) -> tuple[float, dict]:
    """Cosine similarity of resume vs job description. Base 75 if no JD."""
    if not job_description or not job_description.strip():
        return 75.0, {"note": "No job description provided; using base score"}

    resume_tf = _tokenize(raw_text or "")
    jd_tf = _tokenize(job_description)

    similarity = cosine_similarity(resume_tf, jd_tf)
    score = min(100.0, similarity * 200)  # scale: 0.5 cosine → 100

    # Find matching/missing keywords from JD
    jd_keywords = set(k for k in jd_tf if len(k) > 3 and k not in {
        "that", "this", "with", "from", "have", "will", "your", "their",
        "they", "what", "when", "where", "which", "about", "into", "been",
    })
    resume_words = set(resume_tf.keys())
    matched_kw = list(jd_keywords & resume_words)[:20]
    missing_kw = list(jd_keywords - resume_words)[:20]

    return score, {
        "cosine_similarity": round(similarity, 4),
        "matched_keywords": matched_kw,
        "missing_keywords": missing_kw,
    }


# ─── Main analyzer ────────────────────────────────────────────────────────────

class ResumeAnalysisResult:
    """Result container for ATS analysis."""

    def __init__(
        self,
        structure_score: float,
        formatting_score: float,
        keyword_score: float,
        skills_score: float,
        projects_score: float,
        experience_score: float,
        education_score: float,
        contact_score: float,
        job_alignment_score: float,
        analysis_data: dict,
        recommendations: list,
    ):
        self.structure_score = round(structure_score, 1)
        self.formatting_score = round(formatting_score, 1)
        self.keyword_score = round(keyword_score, 1)
        self.skills_score = round(skills_score, 1)
        self.projects_score = round(projects_score, 1)
        self.experience_score = round(experience_score, 1)
        self.education_score = round(education_score, 1)
        self.contact_score = round(contact_score, 1)
        self.job_alignment_score = round(job_alignment_score, 1)
        self.analysis_data = analysis_data
        self.recommendations = recommendations

        # Weighted overall score
        raw = (
            structure_score * WEIGHTS["structure"]
            + formatting_score * WEIGHTS["formatting"]
            + keyword_score * WEIGHTS["keywords"]
            + skills_score * WEIGHTS["skills"]
            + projects_score * WEIGHTS["projects"]
            + experience_score * WEIGHTS["experience"]
            + education_score * WEIGHTS["education"]
            + contact_score * WEIGHTS["contact"]
            + job_alignment_score * WEIGHTS["job_alignment"]
        )
        self.overall_score = round(min(100.0, raw), 1)


def analyze_resume(parsed_data: dict, job_description: Optional[str] = None) -> ResumeAnalysisResult:
    """
    Main entry point: analyze a parsed resume and return ResumeAnalysisResult.

    :param parsed_data: Output of parser.parse_resume() or builder form data.
    :param job_description: Optional job description text for JD-specific scoring.
    :returns: ResumeAnalysisResult with all scores, analysis details, and recommendations.
    """
    raw_text = parsed_data.get("_raw_text", "") or _flatten_text(parsed_data)

    contact = parsed_data.get("contact") or {}
    if isinstance(contact, dict) and contact.get("__root__"):
        contact = contact["__root__"]

    contact_score, contact_detail = score_contact(contact)
    structure_score, structure_detail = score_structure(parsed_data)
    formatting_score, formatting_detail = score_formatting(raw_text, parsed_data)
    keyword_score, keyword_detail = score_keywords(raw_text, parsed_data)
    skills_score, skills_detail = score_skills(parsed_data)
    projects_score, projects_detail = score_projects(parsed_data)
    experience_score, experience_detail = score_experience(parsed_data)
    education_score, education_detail = score_education(parsed_data)
    job_alignment_score, job_detail = score_job_alignment(raw_text, job_description)

    analysis_data = {
        "contact": contact_detail,
        "structure": structure_detail,
        "formatting": formatting_detail,
        "keywords": keyword_detail,
        "skills": skills_detail,
        "projects": projects_detail,
        "experience": experience_detail,
        "education": education_detail,
        "job_alignment": job_detail,
    }

    scores = {
        "structure": structure_score,
        "formatting": formatting_score,
        "keywords": keyword_score,
        "skills": skills_score,
        "projects": projects_score,
        "experience": experience_score,
        "education": education_score,
        "contact": contact_score,
        "job_alignment": job_alignment_score,
    }

    recommendations = generate_recommendations(scores, analysis_data, parsed_data, job_description)

    return ResumeAnalysisResult(
        structure_score=structure_score,
        formatting_score=formatting_score,
        keyword_score=keyword_score,
        skills_score=skills_score,
        projects_score=projects_score,
        experience_score=experience_score,
        education_score=education_score,
        contact_score=contact_score,
        job_alignment_score=job_alignment_score,
        analysis_data=analysis_data,
        recommendations=recommendations,
    )
