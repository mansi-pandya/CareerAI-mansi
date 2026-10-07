"""
Opportunity Extractor
Supports: plain text, URL, image (OCR via pytesseract), PDF (via PyMuPDF/fitz).
"""
import re
from typing import Optional, Tuple

from app.schemas.opportunities import ExtractedOpportunityData


# ─── Regex helpers ────────────────────────────────────────────────────────────

_RE_EMAIL = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE
)
_RE_URL = re.compile(
    r"https?://[^\s\)\]>\"\']+", re.IGNORECASE
)
_RE_SALARY_INR = re.compile(
    r"(?:INR|Rs\.?|₹)\s*(\d[\d,]*(?:\.\d+)?)\s*(?:[-–to]+\s*(?:INR|Rs\.?|₹)?\s*(\d[\d,]*(?:\.\d+)?))?",
    re.IGNORECASE,
)
_RE_SALARY_LPA = re.compile(
    r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*(?:LPA|lpa|L\s*PA)",
    re.IGNORECASE,
)
_RE_SALARY_USD = re.compile(
    r"\$\s*(\d[\d,]*(?:\.\d+)?)[kK]?\s*(?:[-–to]+\s*\$?\s*(\d[\d,]*(?:\.\d+)?)[kK]?)?",
    re.IGNORECASE,
)
_RE_EXPERIENCE = re.compile(
    r"(\d+(?:\.\d+)?)\s*[-–+]?\s*(?:(\d+(?:\.\d+)?)\s*)?(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp\.?)?",
    re.IGNORECASE,
)
_RE_DEADLINE = re.compile(
    r"(?:apply\s+by|last\s+date|deadline)[:\s]+([A-Za-z0-9,\s/\-]+)",
    re.IGNORECASE,
)

_JOB_TYPE_KEYWORDS = {
    "full-time": ["full.time", "full time"],
    "part-time": ["part.time", "part time"],
    "internship": ["intern(?:ship)?"],
    "contract": ["contract", "freelance"],
    "remote": ["remote", "work.from.home", "wfh"],
    "hybrid": ["hybrid"],
}

_SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node", "nodejs", "express", "django", "flask", "fastapi", "spring",
    "sql", "mysql", "postgresql", "mongodb", "redis", "aws", "azure", "gcp",
    "docker", "kubernetes", "git", "linux", "machine learning", "deep learning",
    "tensorflow", "pytorch", "data science", "data analysis", "excel", "power bi",
    "tableau", "figma", "photoshop", "html", "css", "c\\+\\+", "c#", "golang",
    "rust", "kotlin", "swift", "flutter", "react native", "android", "ios",
    "devops", "ci/cd", "jenkins", "ansible", "terraform", "spark", "hadoop",
    "nlp", "computer vision", "blockchain", "solidity",
]
_RE_SKILLS = re.compile(
    r"\b(" + "|".join(_SKILL_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

_EDUCATION_KEYWORDS = re.compile(
    r"\b(b\.?tech|b\.?e|b\.?sc|m\.?tech|m\.?e|m\.?sc|mba|bca|mca|"
    r"bachelor|master|phd|doctorate|diploma|12th|10\+2|graduate|post.?graduate)\b",
    re.IGNORECASE,
)

_COMPANY_PREFIXES = re.compile(
    r"(?:company|employer|organization|at)\s*[:\-]?\s*([A-Z][A-Za-z0-9 &.,\-]{2,50})",
    re.IGNORECASE,
)
_ROLE_PREFIXES = re.compile(
    r"(?:position|role|title|job title|designation|hiring for|opening for)\s*[:\-]?\s*([A-Za-z][A-Za-z0-9 /,\-]{2,60})",
    re.IGNORECASE,
)
_LOCATION_PREFIXES = re.compile(
    r"(?:location|place|city|office)\s*[:\-]?\s*([A-Za-z][A-Za-z0-9 ,\-]{2,60})",
    re.IGNORECASE,
)


def _parse_salary(text: str):
    """Return (min, max, currency) or (None, None, None)."""
    # LPA (Lakhs Per Annum)
    m = _RE_SALARY_LPA.search(text)
    if m:
        lo = float(m.group(1)) * 100_000
        hi = float(m.group(2)) * 100_000
        return lo, hi, "INR"
    # INR explicit
    m = _RE_SALARY_INR.search(text)
    if m:
        lo = float(m.group(1).replace(",", ""))
        hi = float(m.group(2).replace(",", "")) if m.group(2) else lo
        return lo, hi, "INR"
    # USD
    m = _RE_SALARY_USD.search(text)
    if m:
        factor = 1000 if re.search(r"[kK]", text[m.start():m.end()]) else 1
        lo = float(m.group(1).replace(",", "")) * factor
        hi = float(m.group(2).replace(",", "")) * factor if m.group(2) else lo
        return lo, hi, "USD"
    return None, None, None


def extract_from_text(text: str) -> ExtractedOpportunityData:
    """Extract structured opportunity data from plain text using regex patterns."""
    # Company
    company = None
    cm = _COMPANY_PREFIXES.search(text)
    if cm:
        company = cm.group(1).strip().rstrip(".,")

    # Role
    role = None
    rm = _ROLE_PREFIXES.search(text)
    if rm:
        role = rm.group(1).strip().rstrip(".,")

    # Location
    location = None
    lm = _LOCATION_PREFIXES.search(text)
    if lm:
        location = lm.group(1).strip().rstrip(".,")

    # Salary
    sal_min, sal_max, sal_currency = _parse_salary(text)

    # Job type
    job_type = None
    for label, patterns in _JOB_TYPE_KEYWORDS.items():
        combined = re.compile(r"\b(?:" + "|".join(patterns) + r")\b", re.IGNORECASE)
        if combined.search(text):
            job_type = label
            break

    # Skills
    found_skills = list(dict.fromkeys(
        s.lower() for s in _RE_SKILLS.findall(text)
    ))

    # Education
    edu = None
    em = _EDUCATION_KEYWORDS.search(text)
    if em:
        edu = em.group(0).strip()

    # Experience
    exp = None
    xm = _RE_EXPERIENCE.search(text)
    if xm:
        exp = xm.group(0).strip()

    # Deadline
    deadline = None
    dm = _RE_DEADLINE.search(text)
    if dm:
        deadline = dm.group(1).strip()[:30]

    # Email
    emails = _RE_EMAIL.findall(text)
    contact_email = emails[0] if emails else None

    # Application URL (prefer apply/career links)
    app_url = None
    urls = _RE_URL.findall(text)
    for u in urls:
        if any(kw in u.lower() for kw in ["apply", "career", "job", "linkedin", "naukri", "indeed"]):
            app_url = u
            break
    if not app_url and urls:
        app_url = urls[0]

    return ExtractedOpportunityData(
        company=company,
        role=role,
        location=location,
        salary_min=sal_min,
        salary_max=sal_max,
        salary_currency=sal_currency,
        job_type=job_type,
        skills_required=found_skills,
        education_required=edu,
        experience_required=exp,
        deadline=deadline,
        application_url=app_url,
        contact_email=contact_email,
        source_text=text[:1000],
    )


async def extract_from_url(url: str) -> Tuple[Optional[str], ExtractedOpportunityData]:
    """
    Fetch a URL and extract opportunity data from its text content.
    Returns (error_message_or_None, ExtractedOpportunityData).
    """
    try:
        import httpx
    except ImportError:
        return "httpx is not installed", ExtractedOpportunityData(source_text=url)

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "CareerAI-Bot/1.0 (opportunity checker)"},
            )
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "text" not in content_type and "html" not in content_type:
                return "URL does not return readable text content", ExtractedOpportunityData(source_text=url)
            raw = resp.text
    except httpx.TimeoutException:
        return "Request timed out after 30 seconds", ExtractedOpportunityData(source_text=url)
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}", ExtractedOpportunityData(source_text=url)
    except Exception as e:
        return f"Failed to fetch URL: {str(e)}", ExtractedOpportunityData(source_text=url)

    # Strip HTML tags crudely for regex extraction
    clean = re.sub(r"<[^>]+>", " ", raw)
    clean = re.sub(r"\s+", " ", clean).strip()

    data = extract_from_text(clean)
    data.source_text = clean[:1000]
    # Prefer the submitted URL as application URL if none found
    if not data.application_url:
        data.application_url = url
    return None, data


def extract_from_image(image_bytes: bytes, content_type: str = "image/jpeg") -> Tuple[str, ExtractedOpportunityData]:
    """
    OCR an image using pytesseract.
    Returns (ocr_text, ExtractedOpportunityData).
    If tesseract is unavailable returns a graceful degradation message.
    """
    try:
        import pytesseract
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        ocr_text = pytesseract.image_to_string(img)
        data = extract_from_text(ocr_text)
        data.source_text = ocr_text[:1000]
        return ocr_text, data
    except ImportError:
        msg = "OCR requires Tesseract installation. Use text input instead."
        return msg, ExtractedOpportunityData(source_text=msg)
    except Exception as e:
        msg = f"OCR failed: {str(e)}. Use text input instead."
        return msg, ExtractedOpportunityData(source_text=msg)


def extract_from_pdf(pdf_bytes: bytes) -> Tuple[str, ExtractedOpportunityData]:
    """
    Extract text from a PDF using PyMuPDF (fitz).
    Returns (full_text, ExtractedOpportunityData).
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        full_text = "\n".join(pages_text).strip()
    except ImportError:
        full_text = "PDF parsing requires PyMuPDF (fitz). Install with: pip install pymupdf"
    except Exception as e:
        full_text = f"PDF extraction failed: {str(e)}"

    data = extract_from_text(full_text)
    data.source_text = full_text[:1000]
    return full_text, data
