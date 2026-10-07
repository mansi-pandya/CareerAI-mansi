"""
Opportunity Verifier
Runs automated signal-based checks on extracted opportunity data.
NEVER labels anything as "fraud" — uses "Warning Signs Detected" language.
Always includes a disclaimer that results are automated only.
"""
import re
from typing import Optional
from urllib.parse import urlparse

from app.schemas.opportunities import ExtractedOpportunityData, VerificationResult
from app.models.opportunities import VerificationStatusEnum


# Known legitimate job boards — treat as strong positive signal
_LEGITIMATE_DOMAINS = {
    "linkedin.com",
    "naukri.com",
    "indeed.com",
    "glassdoor.com",
    "shine.com",
    "monster.com",
    "instahyre.com",
    "internshala.com",
    "wellfound.com",         # AngelList
    "hirist.tech",
    "foundit.in",
    "timesjobs.com",
    "careers.google.com",
    "careers.microsoft.com",
    "amazon.jobs",
    "jobs.lever.co",
    "boards.greenhouse.io",
    "myworkday.com",
    "jobs.smartrecruiters.com",
    "jobs.ashbyhq.com",
}

# Suspicious TLDs often used in scam sites
_SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".click", ".top", ".loan", ".work"}

# URL shortener domains
_URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "short.io", "rb.gy",
}

# Free email providers — warning for corporate job contact
_FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "yahoo.co.in", "hotmail.com",
    "outlook.com", "rediffmail.com", "ymail.com",
}

# Phrases that indicate the applicant must pay
_PAY_TO_APPLY_PATTERNS = re.compile(
    r"\b(?:registration\s+fee|training\s+fee|pay\s+to\s+apply|"
    r"processing\s+fee|security\s+deposit|refundable\s+deposit|"
    r"pay\s+first|advance\s+payment)\b",
    re.IGNORECASE,
)

# Sensitive personal data asked upfront
_SENSITIVE_INFO_PATTERNS = re.compile(
    r"\b(?:aadhaar|aadhar|pan\s+card|passport\s+number|"
    r"bank\s+account|account\s+number|ifsc|credit\s+card|"
    r"social\s+security)\b",
    re.IGNORECASE,
)

# Very high salary thresholds that are implausible for entry-level
_ENTRY_LEVEL_KEYWORDS = re.compile(
    r"\b(?:fresher|freshers|0[\-–]1\s+year|entry.?level|no\s+experience\s+required)\b",
    re.IGNORECASE,
)
_INR_SUSPICIOUS_THRESHOLD = 5_000_000   # > 50 LPA for freshers
_USD_SUSPICIOUS_THRESHOLD = 200_000     # > $200k for freshers


def _get_domain(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    try:
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return None


def verify_opportunity(
    extracted_data: ExtractedOpportunityData,
    source_text: Optional[str] = None,
) -> VerificationResult:
    """
    Run all available automated checks and produce a VerificationResult.
    Score starts at 50. Each warning subtracts 15; each positive adds 10.
    Status: ≥70 → genuine, 40–69 → could_not_verify, <40 → warning_signs.
    """
    score = 50
    warning_signs: list[str] = []
    positive_signals: list[str] = []
    checks: dict = {}

    text_blob = " ".join(filter(None, [
        extracted_data.source_text or "",
        source_text or "",
    ]))

    # ── 1. Pay-to-apply check ─────────────────────────────────────────────
    pay_match = _PAY_TO_APPLY_PATTERNS.search(text_blob)
    if pay_match:
        score -= 15
        warning_signs.append(
            f"Mentions payment requirement: \"{pay_match.group(0)}\""
        )
        checks["payment_check"] = "warning"
    else:
        checks["payment_check"] = "pass"

    # ── 2. Domain / URL check ─────────────────────────────────────────────
    app_domain = _get_domain(extracted_data.application_url)
    if app_domain:
        tld = "." + app_domain.rsplit(".", 1)[-1] if "." in app_domain else ""
        if tld in _SUSPICIOUS_TLDS:
            score -= 15
            warning_signs.append(f"Application URL uses a suspicious domain extension ({tld})")
            checks["domain_check"] = "warning"
        elif app_domain in _URL_SHORTENERS:
            score -= 10
            warning_signs.append("Application URL uses a URL shortener — destination is unknown")
            checks["domain_check"] = "warning"
        else:
            checks["domain_check"] = "pass"
    else:
        checks["domain_check"] = "no_url"

    # ── 3. Salary plausibility check ──────────────────────────────────────
    sal_max = extracted_data.salary_max
    is_entry = bool(_ENTRY_LEVEL_KEYWORDS.search(text_blob))
    if sal_max and is_entry:
        currency = (extracted_data.salary_currency or "").upper()
        if currency == "INR" and sal_max > _INR_SUSPICIOUS_THRESHOLD:
            score -= 15
            warning_signs.append(
                f"Salary of ₹{sal_max/100_000:.0f}L claimed for entry-level position — unusually high"
            )
            checks["salary_check"] = "warning"
        elif currency == "USD" and sal_max > _USD_SUSPICIOUS_THRESHOLD:
            score -= 15
            warning_signs.append(
                f"Salary of ${sal_max:,.0f} claimed for entry-level position — unusually high"
            )
            checks["salary_check"] = "warning"
        else:
            checks["salary_check"] = "pass"
    else:
        checks["salary_check"] = "not_applicable"

    # ── 4. Contact email check ────────────────────────────────────────────
    contact = extracted_data.contact_email
    if contact:
        email_domain = contact.split("@")[-1].lower() if "@" in contact else ""
        if email_domain in _FREE_EMAIL_DOMAINS:
            score -= 15
            warning_signs.append(
                f"Contact email uses a free email provider ({email_domain}) — unusual for corporate hiring"
            )
            checks["contact_check"] = "warning"
        else:
            score += 5
            positive_signals.append(f"Contact is a corporate email domain ({email_domain})")
            checks["contact_check"] = "positive"
    else:
        checks["contact_check"] = "no_email"

    # ── 5. Sensitive information check ────────────────────────────────────
    sens_match = _SENSITIVE_INFO_PATTERNS.search(text_blob)
    if sens_match:
        score -= 15
        warning_signs.append(
            f"Requests sensitive personal information upfront: \"{sens_match.group(0)}\""
        )
        checks["sensitive_info_check"] = "warning"
    else:
        checks["sensitive_info_check"] = "pass"

    # ── 6. Company ↔ domain consistency check ────────────────────────────
    if app_domain and extracted_data.company:
        company_slug = re.sub(r"[^a-z0-9]", "", extracted_data.company.lower())
        domain_slug = re.sub(r"[^a-z0-9]", "", app_domain.split(".")[0])
        if company_slug and domain_slug and company_slug[:6] in domain_slug:
            score += 5
            positive_signals.append("Company name is consistent with the application URL domain")
            checks["consistency_check"] = "positive"
        else:
            checks["consistency_check"] = "inconclusive"
    else:
        checks["consistency_check"] = "not_applicable"

    # ── 7. Known legitimate job board check ──────────────────────────────
    if app_domain:
        matched_board = next(
            (d for d in _LEGITIMATE_DOMAINS if app_domain == d or app_domain.endswith("." + d)),
            None,
        )
        if matched_board:
            score += 10
            positive_signals.append(f"Application hosted on a known job board ({matched_board})")
            checks["legitimate_url_check"] = "positive"
        else:
            checks["legitimate_url_check"] = "not_matched"
    else:
        checks["legitimate_url_check"] = "no_url"

    # ── 8. Company website check ──────────────────────────────────────────
    if app_domain and app_domain not in _LEGITIMATE_DOMAINS and app_domain not in _URL_SHORTENERS:
        tld = "." + app_domain.rsplit(".", 1)[-1] if "." in app_domain else ""
        if tld not in _SUSPICIOUS_TLDS:
            score += 5
            positive_signals.append("Application URL appears to be a company website")
            checks["company_website_check"] = "positive"
        else:
            checks["company_website_check"] = "suspicious"
    else:
        checks["company_website_check"] = "not_applicable"

    # ── Clamp score ───────────────────────────────────────────────────────
    score = max(0, min(100, score))

    # ── Determine status ──────────────────────────────────────────────────
    if score >= 70:
        status = VerificationStatusEnum.genuine
        explanation = (
            "The signals observed in this opportunity appear consistent with a genuine posting. "
            "No major red flags were detected."
        )
    elif score >= 40:
        status = VerificationStatusEnum.could_not_verify
        explanation = (
            "Some information could be verified, but not enough signals were present "
            "to fully confirm authenticity. Proceed with caution."
        )
    else:
        status = VerificationStatusEnum.warning_signs
        explanation = (
            "Multiple warning signs were detected in this opportunity. "
            "Exercise significant caution and independently verify before proceeding."
        )

    return VerificationResult(
        status=status,
        score=round(score, 1),
        checks_performed=checks,
        warning_signs=warning_signs,
        positive_signals=positive_signals,
        explanation=explanation,
    )
