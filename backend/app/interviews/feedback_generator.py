"""
Post-interview feedback generator.

Takes all answered questions → computes per-dimension scores →
identifies improvement areas → generates recommendations.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings


# ── Score weights ─────────────────────────────────────────────────────────────
# Final overall_score is a weighted sum of the 7 dimension scores

OVERALL_WEIGHTS = {
    "technical": 0.30,
    "communication": 0.20,
    "relevance": 0.15,
    "problem_solving": 0.15,
    "project_knowledge": 0.10,
    "hr_behavioral": 0.10,
}

# Question-type → score dimension mapping
TYPE_TO_DIMENSION = {
    "technical": "technical",
    "coding": "problem_solving",
    "project": "project_knowledge",
    "hr": "hr_behavioral",
    "behavioral": "hr_behavioral",
}


# ── Learning resources lookup ─────────────────────────────────────────────────

RESOURCE_MAP: Dict[str, str] = {
    "python": "https://docs.python.org/3/tutorial/",
    "javascript": "https://javascript.info/",
    "sql": "https://www.w3schools.com/sql/",
    "react": "https://react.dev/learn",
    "data structures": "https://www.geeksforgeeks.org/data-structures/",
    "algorithms": "https://leetcode.com/explore/",
    "system design": "https://github.com/donnemartin/system-design-primer",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "deep learning": "https://www.deeplearning.ai/",
    "communication": "https://www.coursera.org/learn/communication-skills",
    "behavioral": "https://www.themuse.com/advice/star-interview-method",
    "problem solving": "https://leetcode.com/",
    "project knowledge": "https://www.coursera.org/",
    "git": "https://git-scm.com/book/en/v2",
    "docker": "https://docs.docker.com/get-started/",
    "rest api": "https://restfulapi.net/",
    "hr": "https://www.themuse.com/advice/star-interview-method",
    "soft skills": "https://www.coursera.org/learn/communication-skills",
    "default": "https://www.coursera.org/",
}


def _resource_url(topic: str) -> str:
    topic_lower = topic.lower()
    for key, url in RESOURCE_MAP.items():
        if key in topic_lower:
            return url
    return RESOURCE_MAP["default"]


# ── Score computation ─────────────────────────────────────────────────────────

def _safe_avg(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return round(sum(values) / len(values), 1)


def compute_scores(answers_with_questions: List[Tuple[Dict, Dict]]) -> Dict[str, Optional[float]]:
    """
    answers_with_questions: list of (question_dict, answer_dict) pairs
    question_dict keys: question_type, topic
    answer_dict keys: score, technical_correctness, relevance,
                      communication_quality, completeness
    """
    buckets: Dict[str, List[float]] = {
        "technical": [],
        "problem_solving": [],
        "project_knowledge": [],
        "hr_behavioral": [],
    }
    communication_scores: List[float] = []
    relevance_scores: List[float] = []
    technical_accuracy_scores: List[float] = []

    for question, answer in answers_with_questions:
        if not answer:
            continue
        q_type = question.get("question_type") or question.get("type", "technical")
        dimension = TYPE_TO_DIMENSION.get(q_type, "technical")
        score = answer.get("score", 0) or 0

        buckets[dimension].append(float(score))

        comm = answer.get("communication_quality")
        if comm is not None:
            communication_scores.append(float(comm))

        rel = answer.get("relevance")
        if rel is not None:
            relevance_scores.append(float(rel))

        tech = answer.get("technical_correctness")
        if tech is not None:
            technical_accuracy_scores.append(float(tech))

    technical = _safe_avg(buckets["technical"])
    problem_solving = _safe_avg(buckets["problem_solving"])
    project_knowledge = _safe_avg(buckets["project_knowledge"])
    hr_behavioral = _safe_avg(buckets["hr_behavioral"])
    communication = _safe_avg(communication_scores)
    relevance = _safe_avg(relevance_scores)
    technical_accuracy = _safe_avg(technical_accuracy_scores)

    # Overall weighted average (use 50 as placeholder for missing dimensions)
    def v(x: Optional[float]) -> float:
        return x if x is not None else 50.0

    overall = round(
        v(technical) * OVERALL_WEIGHTS["technical"]
        + v(communication) * OVERALL_WEIGHTS["communication"]
        + v(relevance) * OVERALL_WEIGHTS["relevance"]
        + v(problem_solving) * OVERALL_WEIGHTS["problem_solving"]
        + v(project_knowledge) * OVERALL_WEIGHTS["project_knowledge"]
        + v(hr_behavioral) * OVERALL_WEIGHTS["hr_behavioral"],
        1,
    )

    return {
        "overall_score": overall,
        "technical_score": technical,
        "communication_score": communication,
        "relevance_score": relevance,
        "problem_solving_score": problem_solving,
        "project_knowledge_score": project_knowledge,
        "hr_behavioral_score": hr_behavioral,
        "technical_accuracy_score": technical_accuracy,
    }


# ── Improvement area identification ──────────────────────────────────────────

def _score_to_priority(score: Optional[float]) -> Optional[str]:
    if score is None:
        return None
    if score < 50:
        return "high"
    if score <= 70:
        return "medium"
    return "low"


IMPROVEMENT_TEMPLATES: Dict[str, Dict] = {
    "technical": {
        "area": "Technical Knowledge",
        "explanation_tmpl": (
            "Your technical answers scored {score:.0f}/100. "
            "Strengthen your understanding of core computer science concepts, "
            "language features, and system design principles."
        ),
        "practice": (
            "Review data structures, algorithms, and language-specific features. "
            "Build small projects that apply these concepts. Practice on LeetCode or HackerRank."
        ),
    },
    "communication": {
        "area": "Communication & Articulation",
        "explanation_tmpl": (
            "Your communication score was {score:.0f}/100. "
            "Interviewers look for clear, structured, and well-reasoned responses."
        ),
        "practice": (
            "Use the STAR method (Situation, Task, Action, Result) for behavioral questions. "
            "Practice explaining technical concepts out loud to a friend. "
            "Record yourself answering questions and review for clarity."
        ),
    },
    "relevance": {
        "area": "Answer Relevance",
        "explanation_tmpl": (
            "Relevance scored {score:.0f}/100. "
            "Some answers drifted away from what was asked or missed the main point."
        ),
        "practice": (
            "Read the question carefully before answering. "
            "Pause for 5 seconds to plan your answer. "
            "Start your answer by directly addressing the question."
        ),
    },
    "problem_solving": {
        "area": "Problem Solving & Coding",
        "explanation_tmpl": (
            "Problem-solving score: {score:.0f}/100. "
            "Practice breaking down problems systematically before coding."
        ),
        "practice": (
            "Solve 2–3 LeetCode problems daily. "
            "Think out loud: explain your approach before writing code. "
            "Focus on time/space complexity analysis."
        ),
    },
    "project_knowledge": {
        "area": "Project Knowledge",
        "explanation_tmpl": (
            "Project knowledge score: {score:.0f}/100. "
            "Be ready to deeply discuss your own projects — choices, challenges, and learnings."
        ),
        "practice": (
            "For each project on your resume, prepare to explain: "
            "the problem, your architectural decisions, challenges faced, and results. "
            "Be prepared to justify every technology choice."
        ),
    },
    "hr_behavioral": {
        "area": "HR & Behavioral Skills",
        "explanation_tmpl": (
            "HR/Behavioral score: {score:.0f}/100. "
            "Interviewers use behavioral questions to assess cultural fit and soft skills."
        ),
        "practice": (
            "Prepare 5–7 STAR stories from your experiences. "
            "Practice discussing teamwork, failure, conflict, and growth. "
            "Research common behavioral interview questions."
        ),
    },
}


def _identify_improvements(scores: Dict[str, Optional[float]]) -> List[Dict]:
    """Generate improvement recommendations sorted by priority."""
    dimension_map = {
        "technical_score": "technical",
        "communication_score": "communication",
        "relevance_score": "relevance",
        "problem_solving_score": "problem_solving",
        "project_knowledge_score": "project_knowledge",
        "hr_behavioral_score": "hr_behavioral",
    }

    improvements = []
    for score_key, dim_key in dimension_map.items():
        score = scores.get(score_key)
        priority = _score_to_priority(score)
        if priority is None:
            continue
        template = IMPROVEMENT_TEMPLATES[dim_key]
        effective_score = score if score is not None else 50.0
        improvements.append({
            "priority": priority,
            "area": template["area"],
            "topic": dim_key.replace("_", " ").title(),
            "explanation": template["explanation_tmpl"].format(score=effective_score),
            "practice_suggestion": template["practice"],
            "learning_resource_url": _resource_url(dim_key),
        })

    # Sort: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    improvements.sort(key=lambda x: priority_order[x["priority"]])
    return improvements[:5]  # Return at most 5


# ── Summary text generation ───────────────────────────────────────────────────

async def _ai_summary(
    scores: Dict[str, Optional[float]],
    career: str,
    interview_type: str,
    improvements: List[Dict],
) -> Optional[str]:
    """Generate a narrative summary using AI. Returns None on failure."""
    if not settings.AI_API_KEY:
        return None

    try:
        import httpx

        top_improvements = [imp["area"] for imp in improvements[:3]]
        msg = (
            f"Career target: {career}, Interview type: {interview_type}\n"
            f"Scores: {json.dumps({k: v for k, v in scores.items() if v is not None})}\n"
            f"Top improvement areas: {', '.join(top_improvements)}\n"
            "Write a 2–3 sentence personalised interview feedback summary for this student. "
            "Be specific, encouraging, and actionable."
        )

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{settings.AI_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [{"role": "user", "content": msg}],
                    "temperature": 0.6,
                    "max_tokens": 200,
                },
            )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    except Exception:
        return None


def _template_summary(scores: Dict[str, Optional[float]], career: str) -> str:
    overall = scores.get("overall_score", 50) or 50
    if overall >= 80:
        tier = "strong"
        msg = (
            f"Excellent performance! You demonstrated strong readiness for a {career} role. "
            "Keep practising to maintain and sharpen your skills."
        )
    elif overall >= 60:
        tier = "good"
        msg = (
            f"Good interview performance for a {career} role. "
            "You have solid foundational skills with specific areas to strengthen. "
            "Focus on the improvement recommendations below."
        )
    elif overall >= 40:
        tier = "developing"
        msg = (
            f"You showed some good understanding of {career} concepts, "
            "but there are several important areas that need improvement. "
            "Work through the recommendations and practise regularly."
        )
    else:
        tier = "needs work"
        msg = (
            f"This interview highlighted areas that need significant work before you are ready "
            f"for a {career} role. Use the improvement plan below and practise consistently."
        )
    return msg


# ── Public API ────────────────────────────────────────────────────────────────

async def generate_feedback(
    answers_with_questions: List[Tuple[Dict, Dict]],
    career: str,
    interview_type: str,
) -> Dict[str, Any]:
    """
    Generate comprehensive post-interview feedback.

    answers_with_questions: list of (question_dict, answer_dict)
    Returns dict with: scores dict + feedback_summary + improvements list.
    """
    scores = compute_scores(answers_with_questions)
    improvements = _identify_improvements(scores)

    # Try AI summary, fall back to template
    summary = await _ai_summary(scores, career, interview_type, improvements)
    if not summary:
        summary = _template_summary(scores, career)

    return {
        **scores,
        "feedback_summary": summary,
        "improvements": improvements,
    }
