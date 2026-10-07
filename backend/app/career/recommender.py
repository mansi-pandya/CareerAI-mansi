"""
Career recommendation engine.

Scoring weights:
  skill_score       40%
  project_score     20%
  education_score   15%
  experience_score  15%
  interest_score    10%
"""
from __future__ import annotations

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# ── Career profiles ──────────────────────────────────────────────────────────

CAREER_PROFILES: Dict[str, Dict[str, Any]] = {
    "software-engineer": {
        "name": "Software Engineer",
        "industry": "Technology",
        "description": (
            "Design, develop, and maintain software systems. Work across the full stack "
            "on applications ranging from embedded systems to cloud-native services."
        ),
        "required_skills": [
            "python", "java", "c++", "javascript", "data structures", "algorithms",
            "git", "sql", "object-oriented programming", "linux",
        ],
        "preferred_skills": [
            "typescript", "docker", "kubernetes", "rest api", "microservices",
            "system design", "agile", "ci/cd", "testing",
        ],
        "keywords": [
            "software", "application", "system", "backend", "api", "server",
            "development", "programming", "code", "engineering",
        ],
        "education_fields": ["computer science", "software engineering", "information technology"],
        "education_weight": 0.8,
        "avg_salary_min": 85000,
        "avg_salary_max": 160000,
        "market_demand_score": 9.2,
        "growth_rate": 25.0,
    },
    "frontend-developer": {
        "name": "Frontend Developer",
        "industry": "Technology",
        "description": (
            "Build the user-facing side of web applications. Translate UI/UX designs "
            "into responsive, accessible, and performant web interfaces."
        ),
        "required_skills": [
            "html", "css", "javascript", "react", "responsive design", "git",
            "typescript", "rest api",
        ],
        "preferred_skills": [
            "vue", "angular", "tailwind css", "webpack", "vite", "testing",
            "accessibility", "figma", "performance optimization",
        ],
        "keywords": [
            "frontend", "ui", "web", "react", "html", "css", "interface",
            "browser", "client-side", "design system",
        ],
        "education_fields": ["computer science", "web development", "software engineering"],
        "education_weight": 0.6,
        "avg_salary_min": 75000,
        "avg_salary_max": 140000,
        "market_demand_score": 8.5,
        "growth_rate": 16.0,
    },
    "backend-developer": {
        "name": "Backend Developer",
        "industry": "Technology",
        "description": (
            "Design and implement server-side logic, databases, and APIs that power "
            "web and mobile applications."
        ),
        "required_skills": [
            "python", "java", "node.js", "sql", "rest api", "git",
            "databases", "authentication", "linux",
        ],
        "preferred_skills": [
            "postgresql", "redis", "docker", "microservices", "graphql",
            "message queues", "caching", "security", "performance",
        ],
        "keywords": [
            "backend", "server", "api", "database", "sql", "python",
            "node", "microservice", "rest", "auth",
        ],
        "education_fields": ["computer science", "software engineering", "information systems"],
        "education_weight": 0.8,
        "avg_salary_min": 80000,
        "avg_salary_max": 155000,
        "market_demand_score": 9.0,
        "growth_rate": 22.0,
    },
    "full-stack-developer": {
        "name": "Full Stack Developer",
        "industry": "Technology",
        "description": (
            "Build both client-side and server-side software. Work on databases, "
            "servers, systems engineering, and clients."
        ),
        "required_skills": [
            "html", "css", "javascript", "react", "python", "sql",
            "rest api", "git", "databases",
        ],
        "preferred_skills": [
            "typescript", "node.js", "docker", "postgresql", "redis",
            "testing", "ci/cd", "cloud", "microservices",
        ],
        "keywords": [
            "fullstack", "full stack", "frontend", "backend", "web", "react",
            "node", "api", "database", "end-to-end",
        ],
        "education_fields": ["computer science", "web development", "software engineering"],
        "education_weight": 0.7,
        "avg_salary_min": 80000,
        "avg_salary_max": 155000,
        "market_demand_score": 9.1,
        "growth_rate": 23.0,
    },
    "data-analyst": {
        "name": "Data Analyst",
        "industry": "Data & Analytics",
        "description": (
            "Collect, process, and analyze data to help organizations make better "
            "decisions. Create visualizations and reports."
        ),
        "required_skills": [
            "python", "sql", "excel", "data visualization", "statistics",
            "pandas", "tableau", "data cleaning",
        ],
        "preferred_skills": [
            "power bi", "r", "machine learning", "numpy", "matplotlib",
            "seaborn", "business intelligence", "a/b testing",
        ],
        "keywords": [
            "data", "analytics", "sql", "excel", "visualization", "reporting",
            "insight", "dashboard", "business intelligence", "statistics",
        ],
        "education_fields": ["data science", "statistics", "mathematics", "computer science", "business analytics"],
        "education_weight": 0.7,
        "avg_salary_min": 65000,
        "avg_salary_max": 120000,
        "market_demand_score": 8.8,
        "growth_rate": 23.0,
    },
    "data-scientist": {
        "name": "Data Scientist",
        "industry": "Data & Analytics",
        "description": (
            "Apply statistical, mathematical, and machine learning techniques to "
            "extract insights and build predictive models from large datasets."
        ),
        "required_skills": [
            "python", "machine learning", "statistics", "sql", "pandas",
            "numpy", "scikit-learn", "data visualization", "feature engineering",
        ],
        "preferred_skills": [
            "tensorflow", "pytorch", "deep learning", "nlp", "r",
            "spark", "cloud", "experiment design", "a/b testing",
        ],
        "keywords": [
            "data science", "machine learning", "model", "prediction", "statistics",
            "nlp", "deep learning", "feature", "training", "analysis",
        ],
        "education_fields": ["data science", "statistics", "computer science", "mathematics", "physics"],
        "education_weight": 0.9,
        "avg_salary_min": 95000,
        "avg_salary_max": 180000,
        "market_demand_score": 9.0,
        "growth_rate": 35.0,
    },
    "machine-learning-engineer": {
        "name": "Machine Learning Engineer",
        "industry": "Artificial Intelligence",
        "description": (
            "Design and build ML systems that can be deployed at scale. Bridge the gap "
            "between data science research and production engineering."
        ),
        "required_skills": [
            "python", "machine learning", "tensorflow", "pytorch", "scikit-learn",
            "sql", "docker", "mlops", "model deployment",
        ],
        "preferred_skills": [
            "kubernetes", "spark", "deep learning", "feature engineering",
            "cloud", "ci/cd", "distributed computing", "model monitoring",
        ],
        "keywords": [
            "machine learning", "ml", "model", "training", "tensorflow", "pytorch",
            "deployment", "mlops", "pipeline", "inference",
        ],
        "education_fields": ["computer science", "machine learning", "statistics", "mathematics"],
        "education_weight": 0.9,
        "avg_salary_min": 110000,
        "avg_salary_max": 200000,
        "market_demand_score": 9.5,
        "growth_rate": 40.0,
    },
    "ai-engineer": {
        "name": "AI Engineer",
        "industry": "Artificial Intelligence",
        "description": (
            "Build intelligent systems leveraging large language models, generative AI, "
            "and AI APIs to create next-generation products."
        ),
        "required_skills": [
            "python", "llm", "prompt engineering", "langchain", "openai api",
            "machine learning", "rest api", "docker",
        ],
        "preferred_skills": [
            "vector databases", "rag", "fine-tuning", "hugging face",
            "kubernetes", "cloud", "fastapi", "deep learning",
        ],
        "keywords": [
            "ai", "llm", "gpt", "generative", "langchain", "rag", "agent",
            "embedding", "nlp", "intelligent",
        ],
        "education_fields": ["computer science", "artificial intelligence", "machine learning"],
        "education_weight": 0.85,
        "avg_salary_min": 120000,
        "avg_salary_max": 220000,
        "market_demand_score": 9.8,
        "growth_rate": 50.0,
    },
    "cloud-engineer": {
        "name": "Cloud Engineer",
        "industry": "Cloud & Infrastructure",
        "description": (
            "Design, implement, and manage cloud infrastructure on platforms like AWS, "
            "Azure, and GCP. Ensure scalability, reliability, and cost efficiency."
        ),
        "required_skills": [
            "aws", "azure", "gcp", "terraform", "docker", "kubernetes",
            "linux", "networking", "iam", "cloud architecture",
        ],
        "preferred_skills": [
            "ci/cd", "python", "bash", "monitoring", "cost optimization",
            "multi-cloud", "serverless", "cloudformation",
        ],
        "keywords": [
            "cloud", "aws", "azure", "gcp", "infrastructure", "terraform",
            "kubernetes", "serverless", "devops", "scale",
        ],
        "education_fields": ["computer science", "information technology", "networking", "cloud computing"],
        "education_weight": 0.7,
        "avg_salary_min": 95000,
        "avg_salary_max": 175000,
        "market_demand_score": 9.3,
        "growth_rate": 30.0,
    },
    "devops-engineer": {
        "name": "DevOps Engineer",
        "industry": "Cloud & Infrastructure",
        "description": (
            "Bridge development and operations. Automate and streamline build, test, "
            "and deployment pipelines to enable rapid, reliable software delivery."
        ),
        "required_skills": [
            "docker", "kubernetes", "ci/cd", "linux", "git", "bash",
            "terraform", "monitoring", "jenkins",
        ],
        "preferred_skills": [
            "aws", "ansible", "python", "prometheus", "grafana",
            "security", "cost optimization", "site reliability",
        ],
        "keywords": [
            "devops", "ci/cd", "pipeline", "deployment", "automation",
            "docker", "kubernetes", "infrastructure", "reliability", "build",
        ],
        "education_fields": ["computer science", "information technology", "software engineering"],
        "education_weight": 0.7,
        "avg_salary_min": 90000,
        "avg_salary_max": 165000,
        "market_demand_score": 9.0,
        "growth_rate": 22.0,
    },
    "qa-engineer": {
        "name": "QA Engineer",
        "industry": "Technology",
        "description": (
            "Ensure software quality through systematic testing strategies. Design "
            "test cases, automate test suites, and identify defects."
        ),
        "required_skills": [
            "testing", "selenium", "test automation", "sql", "api testing",
            "bug tracking", "python", "javascript",
        ],
        "preferred_skills": [
            "playwright", "cypress", "jira", "ci/cd", "performance testing",
            "security testing", "mobile testing", "agile",
        ],
        "keywords": [
            "testing", "qa", "quality", "automation", "selenium", "test",
            "bug", "regression", "performance", "validation",
        ],
        "education_fields": ["computer science", "software engineering", "information technology"],
        "education_weight": 0.6,
        "avg_salary_min": 65000,
        "avg_salary_max": 130000,
        "market_demand_score": 7.8,
        "growth_rate": 14.0,
    },
    "mobile-developer": {
        "name": "Mobile Developer",
        "industry": "Technology",
        "description": (
            "Build native or cross-platform mobile applications for iOS and Android, "
            "delivering smooth and intuitive user experiences."
        ),
        "required_skills": [
            "swift", "kotlin", "react native", "flutter", "mobile ui",
            "rest api", "git", "app store deployment",
        ],
        "preferred_skills": [
            "firebase", "push notifications", "in-app purchases", "animations",
            "testing", "performance", "ci/cd",
        ],
        "keywords": [
            "mobile", "ios", "android", "swift", "kotlin", "flutter",
            "react native", "app", "ui", "cross-platform",
        ],
        "education_fields": ["computer science", "software engineering", "mobile computing"],
        "education_weight": 0.7,
        "avg_salary_min": 80000,
        "avg_salary_max": 155000,
        "market_demand_score": 8.6,
        "growth_rate": 20.0,
    },
    "cybersecurity-analyst": {
        "name": "Cybersecurity Analyst",
        "industry": "Cybersecurity",
        "description": (
            "Protect organizational systems from cyber threats. Monitor networks, "
            "respond to incidents, and implement security controls."
        ),
        "required_skills": [
            "networking", "linux", "security monitoring", "siem", "firewalls",
            "incident response", "vulnerability assessment", "python",
        ],
        "preferred_skills": [
            "penetration testing", "ethical hacking", "cryptography",
            "cloud security", "threat intelligence", "forensics",
        ],
        "keywords": [
            "security", "cyber", "hacking", "network", "vulnerability",
            "threat", "incident", "firewall", "soc", "encryption",
        ],
        "education_fields": ["cybersecurity", "information security", "computer science", "networking"],
        "education_weight": 0.8,
        "avg_salary_min": 85000,
        "avg_salary_max": 160000,
        "market_demand_score": 9.4,
        "growth_rate": 32.0,
    },
    "product-manager": {
        "name": "Product Manager",
        "industry": "Product & Business",
        "description": (
            "Define product vision and strategy. Work with engineering, design, and "
            "business stakeholders to ship products users love."
        ),
        "required_skills": [
            "product strategy", "agile", "user research", "roadmapping",
            "data analysis", "stakeholder management", "communication",
        ],
        "preferred_skills": [
            "sql", "a/b testing", "figma", "jira", "python",
            "business analysis", "pricing", "market research",
        ],
        "keywords": [
            "product", "roadmap", "feature", "user", "strategy", "agile",
            "stakeholder", "vision", "prioritization", "launch",
        ],
        "education_fields": ["business", "computer science", "engineering", "mba", "product management"],
        "education_weight": 0.6,
        "avg_salary_min": 90000,
        "avg_salary_max": 175000,
        "market_demand_score": 8.7,
        "growth_rate": 18.0,
    },
    "ui-ux-designer": {
        "name": "UI/UX Designer",
        "industry": "Design",
        "description": (
            "Create user-centred designs for digital products. Conduct user research, "
            "build wireframes, prototypes, and high-fidelity designs."
        ),
        "required_skills": [
            "figma", "ui design", "ux design", "wireframing", "prototyping",
            "user research", "design systems", "accessibility",
        ],
        "preferred_skills": [
            "adobe xd", "sketch", "html", "css", "motion design",
            "usability testing", "information architecture",
        ],
        "keywords": [
            "design", "ui", "ux", "figma", "prototype", "wireframe",
            "user experience", "interface", "visual", "usability",
        ],
        "education_fields": ["design", "graphic design", "human-computer interaction", "psychology"],
        "education_weight": 0.5,
        "avg_salary_min": 70000,
        "avg_salary_max": 140000,
        "market_demand_score": 8.2,
        "growth_rate": 15.0,
    },
}


# ── Proficiency map ──────────────────────────────────────────────────────────

_PROF_TO_LEVEL = {
    "beginner": 1,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}


# ── Result dataclass ─────────────────────────────────────────────────────────

@dataclass
class RecommendationResult:
    career_slug: str
    career_name: str
    industry: str
    match_score: float
    skill_score: float
    education_score: float
    project_score: float
    experience_score: float
    interest_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    reasoning: str
    career_data: Dict[str, Any] = field(default_factory=dict)


# ── Recommender ──────────────────────────────────────────────────────────────

class CareerRecommender:
    """
    Recommends the top-N careers for a student profile.

    All skill names are lower-cased for comparison.
    """

    WEIGHTS = {
        "skill": 0.40,
        "project": 0.20,
        "education": 0.15,
        "experience": 0.15,
        "interest": 0.10,
    }

    def __init__(self):
        self._all_slugs = list(CAREER_PROFILES.keys())
        # Build the global skill vocabulary
        skill_set: set = set()
        for cp in CAREER_PROFILES.values():
            skill_set.update(s.lower() for s in cp["required_skills"])
            skill_set.update(s.lower() for s in cp["preferred_skills"])
        self._vocab = sorted(skill_set)
        self._vocab_index = {s: i for i, s in enumerate(self._vocab)}

    # ── public API ────────────────────────────────────────────────────────────

    def recommend(
        self,
        student_skills: List[Dict[str, Any]],     # [{name, proficiency}, ...]
        education: List[Dict[str, Any]],           # [{degree, field_of_study, gpa}, ...]
        projects: List[str],                       # list of project descriptions / titles
        experience: List[str],                     # list of experience descriptions
        career_preferences: List[str],             # preferred career titles
        preferred_career: Optional[str] = None,   # single preferred career field
        top_n: int = 5,
    ) -> List[RecommendationResult]:
        student_skill_names = [s["name"].lower() for s in student_skills]
        student_skill_map = {
            s["name"].lower(): _PROF_TO_LEVEL.get(s.get("proficiency", "beginner"), 1)
            for s in student_skills
        }

        results: List[RecommendationResult] = []
        for slug, profile in CAREER_PROFILES.items():
            result = self._score_career(
                slug, profile,
                student_skill_names, student_skill_map,
                education, projects, experience,
                career_preferences, preferred_career,
            )
            results.append(result)

        # Sort descending by composite match score
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results[:top_n]

    # ── scoring helpers ───────────────────────────────────────────────────────

    def _score_career(
        self,
        slug: str,
        profile: Dict[str, Any],
        student_skill_names: List[str],
        student_skill_map: Dict[str, int],
        education: List[Dict[str, Any]],
        projects: List[str],
        experience: List[str],
        career_preferences: List[str],
        preferred_career: Optional[str],
    ) -> RecommendationResult:
        req = [s.lower() for s in profile["required_skills"]]
        pref = [s.lower() for s in profile["preferred_skills"]]
        all_career_skills = req + pref

        # ── Skill score (cosine similarity on skill vectors) ──────────────────
        student_vec = self._skill_vector(student_skill_names, student_skill_map)
        career_vec = self._career_skill_vector(req, pref)
        if np.any(student_vec) and np.any(career_vec):
            cos_sim = float(cosine_similarity(
                student_vec.reshape(1, -1),
                career_vec.reshape(1, -1),
            )[0][0])
        else:
            cos_sim = 0.0

        matched_skills = [s for s in student_skill_names if s in all_career_skills]
        missing_required = [s for s in req if s not in student_skill_names]
        missing_preferred = [s for s in pref if s not in student_skill_names]
        missing_skills = missing_required + [s for s in missing_preferred if s not in missing_required]

        # Blend cosine with direct coverage ratio
        coverage = len(matched_skills) / max(len(all_career_skills), 1)
        skill_score = min((cos_sim * 0.6 + coverage * 0.4) * 100, 100.0)

        # ── Education score ───────────────────────────────────────────────────
        education_score = self._education_score(education, profile)

        # ── Project score ─────────────────────────────────────────────────────
        project_score = self._keyword_score(projects, profile["keywords"])

        # ── Experience score ──────────────────────────────────────────────────
        experience_score = self._keyword_score(experience, profile["keywords"])

        # ── Interest score ────────────────────────────────────────────────────
        interest_score = self._interest_score(
            career_preferences, preferred_career, slug, profile["name"]
        )

        # ── Composite ────────────────────────────────────────────────────────
        match_score = (
            skill_score * self.WEIGHTS["skill"]
            + project_score * self.WEIGHTS["project"]
            + education_score * self.WEIGHTS["education"]
            + experience_score * self.WEIGHTS["experience"]
            + interest_score * self.WEIGHTS["interest"]
        )
        match_score = round(min(match_score, 100.0), 1)

        reasoning = self._build_reasoning(
            profile["name"], match_score, skill_score,
            matched_skills, missing_required, education_score, interest_score,
        )

        return RecommendationResult(
            career_slug=slug,
            career_name=profile["name"],
            industry=profile["industry"],
            match_score=match_score,
            skill_score=round(skill_score, 1),
            education_score=round(education_score, 1),
            project_score=round(project_score, 1),
            experience_score=round(experience_score, 1),
            interest_score=round(interest_score, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills[:10],
            reasoning=reasoning,
            career_data=profile,
        )

    def _skill_vector(
        self,
        skill_names: List[str],
        skill_map: Dict[str, int],
    ) -> np.ndarray:
        vec = np.zeros(len(self._vocab))
        for s in skill_names:
            if s in self._vocab_index:
                vec[self._vocab_index[s]] = skill_map.get(s, 1)
        return vec

    def _career_skill_vector(
        self,
        required: List[str],
        preferred: List[str],
    ) -> np.ndarray:
        vec = np.zeros(len(self._vocab))
        for s in required:
            if s in self._vocab_index:
                vec[self._vocab_index[s]] = 3    # required weight
        for s in preferred:
            if s in self._vocab_index:
                vec[self._vocab_index[s]] = 1.5  # preferred weight
        return vec

    def _education_score(
        self,
        education: List[Dict[str, Any]],
        profile: Dict[str, Any],
    ) -> float:
        if not education:
            return 30.0  # no education data – give baseline

        best = 0.0
        target_fields = [f.lower() for f in profile["education_fields"]]
        edu_weight = profile["education_weight"]

        for edu in education:
            score = 40.0  # base for having a degree
            field = (edu.get("field_of_study") or "").lower()
            degree = (edu.get("degree") or "").lower()
            gpa = edu.get("gpa") or 0.0

            # Field match
            if any(tf in field for tf in target_fields):
                score += 40.0
            elif any(keyword in field for keyword in ["engineering", "science", "technology"]):
                score += 20.0

            # GPA bonus
            if gpa >= 3.7:
                score += 15.0
            elif gpa >= 3.3:
                score += 10.0
            elif gpa >= 3.0:
                score += 5.0

            # Advanced degree bonus
            if any(x in degree for x in ["master", "phd", "doctorate"]):
                score += 5.0

            score = min(score * edu_weight + score * (1 - edu_weight) * 0.6, 100.0)
            best = max(best, score)

        return round(best, 1)

    def _keyword_score(
        self,
        text_items: List[str],
        keywords: List[str],
    ) -> float:
        if not text_items:
            return 0.0
        combined = " ".join(text_items).lower()
        hits = sum(1 for kw in keywords if kw in combined)
        return round(min((hits / max(len(keywords), 1)) * 100 * 1.5, 100.0), 1)

    def _interest_score(
        self,
        career_preferences: List[str],
        preferred_career: Optional[str],
        slug: str,
        career_name: str,
    ) -> float:
        career_name_lower = career_name.lower()
        slug_lower = slug.lower()

        for pref in career_preferences:
            p = pref.lower()
            if p in career_name_lower or career_name_lower in p or slug_lower in p:
                return 100.0

        if preferred_career:
            p = preferred_career.lower()
            if p in career_name_lower or career_name_lower in p or slug_lower in p:
                return 80.0

        return 0.0

    def _build_reasoning(
        self,
        career_name: str,
        match_score: float,
        skill_score: float,
        matched_skills: List[str],
        missing_required: List[str],
        education_score: float,
        interest_score: float,
    ) -> str:
        parts = []
        if match_score >= 80:
            parts.append(f"Strong fit for {career_name} ({match_score:.0f}% match).")
        elif match_score >= 60:
            parts.append(f"Good potential for {career_name} ({match_score:.0f}% match).")
        else:
            parts.append(f"Developing profile for {career_name} ({match_score:.0f}% match).")

        if matched_skills:
            sample = matched_skills[:4]
            parts.append(f"You already have key skills: {', '.join(sample)}.")

        if missing_required:
            sample = missing_required[:3]
            parts.append(f"Focus on learning: {', '.join(sample)} to strengthen this path.")

        if education_score >= 70:
            parts.append("Your educational background aligns well with this career.")

        if interest_score > 0:
            parts.append("This matches your stated career interests.")

        return " ".join(parts)


# ── Module-level singleton ────────────────────────────────────────────────────
recommender = CareerRecommender()
