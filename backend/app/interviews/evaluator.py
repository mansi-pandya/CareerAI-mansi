"""
Answer evaluation engine.

evaluate_answer(question, answer_text, student_profile) → AnswerFeedback dict.

Evaluation dimensions:
  - technical_correctness (0-100)
  - relevance              (0-100)
  - communication_quality  (0-100)
  - completeness           (0-100)
  - overall_score          weighted average

Falls back to keyword-based evaluation when AI_API_KEY is not set.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from app.core.config import settings


# ── Weights ───────────────────────────────────────────────────────────────────

SCORE_WEIGHTS = {
    "technical_correctness": 0.35,
    "relevance": 0.25,
    "communication_quality": 0.20,
    "completeness": 0.20,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _word_set(text: str) -> set:
    """Lowercase words from text, stripped of punctuation."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _keyword_coverage(answer_words: set, points: List[str]) -> float:
    """Fraction of expected answer points whose keywords appear in the answer."""
    if not points:
        return 0.5  # no reference — neutral
    hits = 0
    for point in points:
        point_words = _word_set(point)
        # A point is "covered" if at least 30 % of its keywords appear in answer
        if point_words:
            overlap = len(point_words & answer_words) / len(point_words)
            if overlap >= 0.3:
                hits += 1
    return hits / len(points)


def _communication_score(answer: str) -> float:
    """
    Rough heuristic for communication quality:
      - Length (50–500 chars sweet spot)
      - Has structure (uses words like "first", "because", "for example")
      - Not just bullet fragments
    """
    length = len(answer.strip())
    if length < 30:
        length_score = 20.0
    elif length < 80:
        length_score = 50.0
    elif length < 200:
        length_score = 70.0
    elif length <= 600:
        length_score = 90.0
    else:
        length_score = 80.0  # slightly penalise rambling

    structure_words = [
        "first", "second", "third", "because", "therefore", "however",
        "for example", "such as", "in addition", "furthermore", "in conclusion",
        "to summarize", "specifically", "as a result", "this means",
    ]
    answer_lower = answer.lower()
    structure_bonus = min(10.0, sum(3 for sw in structure_words if sw in answer_lower))

    return min(100.0, length_score + structure_bonus)


def _keyword_evaluate(
    question: Dict,
    answer_text: str,
) -> Dict:
    """Rule-based evaluation using expected_answer_points."""
    expected_points: List[str] = question.get("expected_answer_points", [])
    question_type = question.get("question_type") or question.get("type", "technical")
    answer_words = _word_set(answer_text)

    coverage = _keyword_coverage(answer_words, expected_points)
    technical_correctness = round(coverage * 100)
    relevance_score = round(min(100, coverage * 110))  # slight boost
    communication = round(_communication_score(answer_text))
    completeness = round(coverage * 100)

    # For HR/behavioral, communication and relevance matter more than exact keywords
    if question_type in ("hr", "behavioral"):
        technical_correctness = min(100, int(coverage * 80) + 20)
        communication = round(_communication_score(answer_text))
        completeness = round(min(100, coverage * 90) + 10)

    # Overall weighted score
    overall = round(
        technical_correctness * SCORE_WEIGHTS["technical_correctness"]
        + relevance_score * SCORE_WEIGHTS["relevance"]
        + communication * SCORE_WEIGHTS["communication_quality"]
        + completeness * SCORE_WEIGHTS["completeness"]
    )

    # Strengths / weaknesses
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_points: List[str] = []

    if communication >= 70:
        strengths.append("Your answer is well-structured and clear.")
    else:
        weaknesses.append("Try to give a more detailed and structured response.")

    if coverage >= 0.7:
        strengths.append("You covered the key concepts well.")
    elif coverage >= 0.4:
        weaknesses.append("You touched on some key points but missed others.")
    else:
        weaknesses.append("The answer is missing important key concepts.")

    # Identify uncovered expected points
    for point in expected_points:
        point_words = _word_set(point)
        if point_words:
            overlap = len(point_words & answer_words) / len(point_words)
            if overlap < 0.3:
                missing_points.append(point)

    if len(answer_text.strip()) < 50:
        weaknesses.append("Your answer is too short — elaborate more to demonstrate knowledge.")

    better_example: Optional[str] = None
    if missing_points:
        better_example = (
            "A stronger answer would also mention: "
            + "; ".join(f"• {p}" for p in missing_points[:3])
        )

    # Build feedback text
    if overall >= 80:
        feedback = "Excellent answer! You demonstrated strong understanding of this topic."
    elif overall >= 60:
        feedback = "Good answer. You covered the main points, but there is room to go deeper."
    elif overall >= 40:
        feedback = "Partial answer. Some key concepts were missing or under-explained."
    else:
        feedback = "This answer needs improvement. Review the core concepts for this topic."

    if missing_points:
        feedback += f" Key points to add: {'; '.join(missing_points[:2])}."

    return {
        "score": overall,
        "feedback": feedback,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "better_answer_example": better_example,
        "technical_correctness": float(technical_correctness),
        "relevance": float(relevance_score),
        "communication_quality": float(communication),
        "completeness": float(completeness),
    }


# ── AI evaluation ─────────────────────────────────────────────────────────────

async def _evaluate_with_ai(
    question: Dict,
    answer_text: str,
    student_profile: Optional[Dict],
) -> Optional[Dict]:
    """Use AI to evaluate an answer. Returns None on failure."""
    if not settings.AI_API_KEY:
        return None

    try:
        import httpx

        system = (
            "You are a senior technical interviewer evaluating a candidate's answer. "
            "Score each dimension on a 0–100 scale and provide actionable feedback. "
            "Output ONLY valid JSON with keys: "
            "technical_correctness, relevance, communication_quality, completeness, "
            "overall_score, feedback, strengths (array), weaknesses (array), better_answer_example."
        )

        user_msg = (
            f"Question: {question.get('question_text') or question.get('text', '')}\n"
            f"Question type: {question.get('question_type') or question.get('type', 'technical')}\n"
            f"Expected key points: {json.dumps(question.get('expected_answer_points', []))}\n"
            f"Candidate's answer: {answer_text}\n"
            "Evaluate the answer and return a JSON object."
        )

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                f"{settings.AI_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 600,
                },
            )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Extract JSON object
        start = content.find("{")
        end = content.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        result = json.loads(content[start:end])

        # Normalise fields
        return {
            "score": float(result.get("overall_score", 50)),
            "feedback": str(result.get("feedback", "")),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "better_answer_example": result.get("better_answer_example"),
            "technical_correctness": float(result.get("technical_correctness", 50)),
            "relevance": float(result.get("relevance", 50)),
            "communication_quality": float(result.get("communication_quality", 50)),
            "completeness": float(result.get("completeness", 50)),
        }

    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

async def evaluate_answer(
    question: Dict,
    answer_text: str,
    student_profile: Optional[Dict] = None,
) -> Dict:
    """
    Evaluate an answer and return a feedback dict.

    question dict must have at minimum:
      - question_text (or text)
      - question_type (or type)
      - expected_answer_points  (list of strings)

    Returns dict with: score, feedback, strengths, weaknesses,
                       better_answer_example, technical_correctness,
                       relevance, communication_quality, completeness.
    """
    # Try AI first
    ai_result = await _evaluate_with_ai(question, answer_text, student_profile)
    if ai_result is not None:
        return ai_result

    # Fallback: keyword-based
    return _keyword_evaluate(question, answer_text)
