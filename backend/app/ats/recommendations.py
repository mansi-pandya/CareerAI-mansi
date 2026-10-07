"""
ATS Recommendations Engine.

Generates concrete, actionable recommendations for each low-scoring
dimension. Each recommendation includes:
  - category
  - current_problem
  - why_it_matters
  - how_to_fix
  - section_to_modify
  - priority ("high" / "medium" / "low")
  - estimated_score_impact (integer points)
"""
from typing import Optional


def _rec(
    category: str,
    current_problem: str,
    why_it_matters: str,
    how_to_fix: str,
    section_to_modify: str,
    priority: str,
    estimated_score_impact: int,
) -> dict:
    return {
        "category": category,
        "current_problem": current_problem,
        "why_it_matters": why_it_matters,
        "how_to_fix": how_to_fix,
        "section_to_modify": section_to_modify,
        "priority": priority,
        "estimated_score_impact": estimated_score_impact,
    }


# ─── Per-dimension recommendation generators ─────────────────────────────────

def _contact_recs(score: float, detail: dict) -> list:
    recs = []
    missing = detail.get("missing", [])

    if "email" in missing:
        recs.append(_rec(
            category="Contact Information",
            current_problem="Your resume is missing an email address.",
            why_it_matters="Recruiters and ATS systems need an email to contact you. Resumes without an email are routinely discarded.",
            how_to_fix="Add your professional email (e.g., yourname@gmail.com) in the contact/header section at the top of your resume.",
            section_to_modify="contact",
            priority="high",
            estimated_score_impact=8,
        ))
    if "phone" in missing:
        recs.append(_rec(
            category="Contact Information",
            current_problem="No phone number was detected on your resume.",
            why_it_matters="Many recruiters prefer calling candidates. A missing phone number limits how they can reach you.",
            how_to_fix="Add your phone number (with country code if applying internationally) in the contact section.",
            section_to_modify="contact",
            priority="high",
            estimated_score_impact=6,
        ))
    if "linkedin" in missing:
        recs.append(_rec(
            category="Contact Information",
            current_problem="No LinkedIn profile URL was found.",
            why_it_matters="83% of recruiters check LinkedIn before interviewing a candidate. Including your profile URL gives them instant access to your professional background.",
            how_to_fix="Create a LinkedIn profile at linkedin.com if you don't have one, then add the URL (e.g., linkedin.com/in/your-name) to your contact section.",
            section_to_modify="contact",
            priority="medium",
            estimated_score_impact=5,
        ))
    if "github" in missing:
        recs.append(_rec(
            category="Contact Information",
            current_problem="No GitHub profile URL was found.",
            why_it_matters="For tech roles, GitHub is your live portfolio. Hiring managers often check it to assess your coding skills and activity.",
            how_to_fix="Add your GitHub profile URL (e.g., github.com/your-username) to the contact section. Make sure your public repositories are up to date.",
            section_to_modify="contact",
            priority="medium",
            estimated_score_impact=4,
        ))
    if "name" in missing:
        recs.append(_rec(
            category="Contact Information",
            current_problem="Your name could not be detected at the top of the resume.",
            why_it_matters="ATS systems and recruiters expect to see the applicant's full name prominently at the top.",
            how_to_fix="Place your full name as the very first line of your resume, in a slightly larger font than the body text.",
            section_to_modify="contact",
            priority="high",
            estimated_score_impact=7,
        ))
    return recs


def _structure_recs(score: float, detail: dict) -> list:
    recs = []
    missing = detail.get("missing", [])

    if "contact" in missing:
        recs.append(_rec(
            category="Resume Structure",
            current_problem="No distinct contact section was detected.",
            why_it_matters="ATS parsers look for a clearly separated contact block. Without it, your details may be missed entirely.",
            how_to_fix="Add a clearly labelled 'Contact' or 'Personal Information' section at the very top with name, email, phone, LinkedIn, and GitHub.",
            section_to_modify="contact",
            priority="high",
            estimated_score_impact=10,
        ))
    if "education" in missing:
        recs.append(_rec(
            category="Resume Structure",
            current_problem="No education section was detected.",
            why_it_matters="Most ATS filters require an education section to match degree requirements. Missing it can auto-disqualify your resume.",
            how_to_fix="Add an 'Education' section listing your degree, institution, graduation year, and CGPA.",
            section_to_modify="education",
            priority="high",
            estimated_score_impact=10,
        ))
    if "skills" in missing:
        recs.append(_rec(
            category="Resume Structure",
            current_problem="No skills section was detected.",
            why_it_matters="ATS systems use keyword matching on the skills section. Without it, your resume may fail automated screening even if you have the right skills.",
            how_to_fix="Add a 'Technical Skills' section with categorized lists: Programming Languages, Frameworks, Databases, Tools, etc.",
            section_to_modify="skills",
            priority="high",
            estimated_score_impact=12,
        ))
    if "projects_or_experience" in missing:
        recs.append(_rec(
            category="Resume Structure",
            current_problem="Neither a projects section nor a work experience section was found.",
            why_it_matters="Without demonstrating practical application of your skills, recruiters have no evidence you can do the job.",
            how_to_fix="Add a 'Projects' section with at least 2–3 projects that show your technical skills. Include project name, brief description, tech stack, and outcome.",
            section_to_modify="projects",
            priority="high",
            estimated_score_impact=15,
        ))
    if "extras" in missing:
        recs.append(_rec(
            category="Resume Structure",
            current_problem="No certifications or achievements section was found.",
            why_it_matters="Certifications and achievements differentiate you from other candidates with similar education.",
            how_to_fix="Add a 'Certifications' section listing relevant courses (Coursera, edX, AWS, etc.) with issuer and date. Add an 'Achievements' section for competition wins, hackathons, or academic honours.",
            section_to_modify="certifications",
            priority="low",
            estimated_score_impact=5,
        ))
    return recs


def _formatting_recs(score: float, detail: dict) -> list:
    recs = []
    notes = detail.get("notes", [])
    word_count = detail.get("word_count", 0)

    if word_count < 200:
        recs.append(_rec(
            category="Resume Formatting",
            current_problem=f"Your resume is too short ({word_count} words). It lacks sufficient detail to be competitive.",
            why_it_matters="Resumes under 300 words are typically seen as incomplete. ATS systems score higher for content-rich resumes.",
            how_to_fix="Expand each section. For projects, add a description, the tech used, and what you achieved. For skills, list all your tools. For education, add coursework. Aim for 400–700 words.",
            section_to_modify="all",
            priority="high",
            estimated_score_impact=15,
        ))
    elif word_count > 2000:
        recs.append(_rec(
            category="Resume Formatting",
            current_problem=f"Your resume is too long ({word_count} words). It may be skipped by time-pressed recruiters.",
            why_it_matters="One-page resumes (or two pages maximum for experienced professionals) are the standard. Overly long resumes show poor prioritization.",
            how_to_fix="Remove redundant phrases, cut job duties that don't highlight impact, and focus on your top 3–5 achievements per role.",
            section_to_modify="all",
            priority="medium",
            estimated_score_impact=8,
        ))

    if not any("bullet" in n.lower() for n in notes):
        recs.append(_rec(
            category="Resume Formatting",
            current_problem="Your resume does not use bullet points for listing responsibilities or achievements.",
            why_it_matters="Bullet points make your resume scannable. ATS systems and recruiters spend 6–10 seconds on a first pass — bullets make information immediately visible.",
            how_to_fix="Replace paragraph-style descriptions with concise bullet points. Start each bullet with an action verb (e.g., 'Developed a REST API that...').",
            section_to_modify="experience",
            priority="medium",
            estimated_score_impact=10,
        ))

    if not any("date" in n.lower() for n in notes):
        recs.append(_rec(
            category="Resume Formatting",
            current_problem="Date formats appear inconsistent or were not detected.",
            why_it_matters="Consistent date formats (e.g., 'Jan 2023 – May 2024') help ATS systems correctly parse your timeline.",
            how_to_fix="Use a consistent date format throughout: 'MMM YYYY – MMM YYYY' (e.g., 'Aug 2022 – May 2024'). Use 'Present' or 'Current' for ongoing roles.",
            section_to_modify="experience",
            priority="low",
            estimated_score_impact=5,
        ))
    return recs


def _keyword_recs(score: float, detail: dict) -> list:
    recs = []
    matched = detail.get("matched", [])
    count = detail.get("count", 0)

    if count < 5:
        recs.append(_rec(
            category="Keyword Optimization",
            current_problem=f"Only {count} common technical keywords were detected. Your resume may be filtered out by ATS keyword matching.",
            why_it_matters="Most ATS systems rank resumes based on keyword density. A resume with fewer relevant keywords ranks lower, even if the candidate is qualified.",
            how_to_fix="Add a comprehensive 'Technical Skills' section. Include all technologies, frameworks, databases, and tools you know — even if you list them later in projects. Common keywords: Python, Java, React, SQL, Docker, Git, AWS, REST API.",
            section_to_modify="skills",
            priority="high",
            estimated_score_impact=15,
        ))
    elif count < 15:
        recs.append(_rec(
            category="Keyword Optimization",
            current_problem=f"Your resume has {count} recognized technical keywords. Adding more relevant terms will improve ATS ranking.",
            why_it_matters="Resumes with 15+ relevant technical keywords consistently score higher in ATS screening for tech roles.",
            how_to_fix="Review your projects and experience. Add specific technologies you used to your Skills section. Include framework versions (e.g., 'React 18', 'Python 3.11') where applicable.",
            section_to_modify="skills",
            priority="medium",
            estimated_score_impact=8,
        ))
    return recs


def _skills_recs(score: float, detail: dict) -> list:
    recs = []
    total = detail.get("total_skills", 0)
    categories = detail.get("categories", 0)

    if total < 8:
        recs.append(_rec(
            category="Skills Section",
            current_problem=f"Only {total} skills are listed. This is insufficient to pass most ATS filters for tech roles.",
            why_it_matters="Technical recruiters expect to see a broad skill set. Fewer than 10 skills signals limited technical knowledge.",
            how_to_fix="List every technology you have used: programming languages, frameworks, libraries, databases, cloud services, and tools. Aim for 20+ skills across at least 4 categories.",
            section_to_modify="skills",
            priority="high",
            estimated_score_impact=12,
        ))
    elif categories < 3:
        recs.append(_rec(
            category="Skills Section",
            current_problem=f"Skills are only listed in {categories} category/categories. Lack of diversity limits your profile.",
            why_it_matters="Full-stack and versatile candidates are more attractive. Categorizing skills also makes them easier for ATS to parse.",
            how_to_fix="Organize skills into categories: Programming Languages, Web Technologies, Databases, Cloud & DevOps, AI/ML Tools, and Development Tools.",
            section_to_modify="skills",
            priority="medium",
            estimated_score_impact=8,
        ))
    return recs


def _projects_recs(score: float, detail: dict) -> list:
    recs = []
    count = detail.get("count", 0)
    issues = detail.get("issues", [])

    if count == 0:
        recs.append(_rec(
            category="Projects",
            current_problem="No projects were found on your resume.",
            why_it_matters="For students and early-career developers, projects are the primary evidence of practical skills. Recruiters expect to see at least 2–3 projects.",
            how_to_fix="Add a 'Projects' section with 3–5 projects. Each should include: project name, 2–3 sentence description, tech stack, GitHub link, and the outcome or impact.",
            section_to_modify="projects",
            priority="high",
            estimated_score_impact=20,
        ))
    else:
        desc_issues = [i for i in issues if "description" in i.lower()]
        tech_issues = [i for i in issues if "tech" in i.lower()]
        if desc_issues:
            recs.append(_rec(
                category="Projects",
                current_problem=f"{len(desc_issues)} project(s) are missing descriptions. Bare project names provide no context.",
                why_it_matters="A description explains what the project does, the problem it solves, and your role — key information for both ATS and human reviewers.",
                how_to_fix="For each project, write 2–3 sentences: what it does, what technologies you used, and what you achieved (e.g., 'Reduced API response time by 40%' or 'Served 500+ daily active users').",
                section_to_modify="projects",
                priority="high",
                estimated_score_impact=12,
            ))
        if tech_issues:
            recs.append(_rec(
                category="Projects",
                current_problem=f"{len(tech_issues)} project(s) are missing tech stack information.",
                why_it_matters="ATS systems match tech stacks mentioned in projects against job requirements. Missing tech stack reduces your keyword score.",
                how_to_fix="Add a 'Tech Stack: ' or 'Built with: ' line to each project listing all libraries, frameworks, and languages used.",
                section_to_modify="projects",
                priority="medium",
                estimated_score_impact=8,
            ))
        if count < 3:
            recs.append(_rec(
                category="Projects",
                current_problem=f"Only {count} project(s) listed. Recruiters for entry-level roles expect 3–5 projects.",
                why_it_matters="More projects demonstrate consistent effort and breadth of skills. A single project doesn't show sustained development ability.",
                how_to_fix="Add 2–3 more projects. These can be course projects, open-source contributions, personal tools, or recreations of existing apps with your own improvements.",
                section_to_modify="projects",
                priority="medium",
                estimated_score_impact=10,
            ))
    return recs


def _experience_recs(score: float, detail: dict) -> list:
    recs = []
    verb_count = detail.get("action_verb_count", 0)
    quant_count = detail.get("quantified_count", 0)

    if verb_count < 4:
        recs.append(_rec(
            category="Work Experience & Descriptions",
            current_problem=f"Only {verb_count} action verb(s) were found in your experience/project descriptions.",
            why_it_matters="Strong action verbs make your contributions sound impactful and professional. ATS systems score for active, achievement-oriented language.",
            how_to_fix="Start every bullet point with a strong action verb: Developed, Built, Designed, Implemented, Optimized, Reduced, Increased, Led, Automated, Deployed. Avoid 'Responsible for' or 'Helped with'.",
            section_to_modify="experience",
            priority="high",
            estimated_score_impact=10,
        ))
    if quant_count < 2:
        recs.append(_rec(
            category="Work Experience & Descriptions",
            current_problem="Very few quantified achievements were found (no metrics like %, users, hours, etc.).",
            why_it_matters="Quantified results demonstrate real impact. 'Improved performance' is forgettable; 'Improved API response time by 45%, reducing page load from 3s to 1.6s' is memorable and credible.",
            how_to_fix="Add numbers to your achievements: users served, performance improvements (%), lines of code, time saved, accuracy rates, team size, deployment frequency. Even estimates are better than none.",
            section_to_modify="experience",
            priority="high",
            estimated_score_impact=12,
        ))
    return recs


def _education_recs(score: float, detail: dict) -> list:
    recs = []
    issues = detail.get("issues", [])

    if "CGPA not found" in issues:
        recs.append(_rec(
            category="Education",
            current_problem="Your CGPA was not found in the education section.",
            why_it_matters="For recent graduates, CGPA is a key screening criterion. Many companies filter for 7.0+ or 3.0+. Not listing it may cause ATS to assign a low education score.",
            how_to_fix="Add your CGPA in the format: 'CGPA: 8.2/10' or 'GPA: 3.6/4.0' directly under your degree and institution.",
            section_to_modify="education",
            priority="medium",
            estimated_score_impact=8,
        ))
    if "Education dates missing" in issues:
        recs.append(_rec(
            category="Education",
            current_problem="Start/end dates for your education are missing.",
            why_it_matters="ATS systems use graduation date to calculate years of experience and verify recency. Missing dates may cause parsing errors.",
            how_to_fix="Add dates in 'Aug 2020 – May 2024' format under each education entry.",
            section_to_modify="education",
            priority="medium",
            estimated_score_impact=5,
        ))
    if detail.get("count", 0) == 0:
        recs.append(_rec(
            category="Education",
            current_problem="No education entries were detected.",
            why_it_matters="Education is one of the first things recruiters check. A missing education section is a serious red flag.",
            how_to_fix="Add your most recent degree: institution name, degree title (e.g., B.Tech Computer Science), start/end dates, and CGPA.",
            section_to_modify="education",
            priority="high",
            estimated_score_impact=15,
        ))
    return recs


def _job_alignment_recs(score: float, detail: dict, job_description: Optional[str]) -> list:
    recs = []
    if not job_description:
        return recs

    missing_kw = detail.get("missing_keywords", [])
    if missing_kw and score < 60:
        kw_sample = ", ".join(missing_kw[:10])
        recs.append(_rec(
            category="Job Description Alignment",
            current_problem=f"Your resume is missing {len(missing_kw)} keywords from the job description.",
            why_it_matters="ATS systems match your resume against the job posting keyword-for-keyword. A low match score means automatic rejection before a human ever reads it.",
            how_to_fix=f"Add missing keywords to relevant sections: {kw_sample}. Mirror the exact phrasing from the job description (e.g., if the JD says 'REST APIs', don't write 'RESTful services').",
            section_to_modify="skills",
            priority="high",
            estimated_score_impact=15,
        ))
    elif missing_kw and score < 80:
        kw_sample = ", ".join(missing_kw[:5])
        recs.append(_rec(
            category="Job Description Alignment",
            current_problem=f"Some keywords from the job description are missing from your resume: {kw_sample}.",
            why_it_matters="Even a 70–80% keyword match may be filtered out in competitive applicant pools. Higher alignment means higher ATS ranking.",
            how_to_fix=f"Include these terms naturally in your skills or project descriptions: {kw_sample}.",
            section_to_modify="skills",
            priority="medium",
            estimated_score_impact=8,
        ))
    return recs


# ─── Main generator ───────────────────────────────────────────────────────────

def generate_recommendations(
    scores: dict,
    analysis_data: dict,
    parsed_data: dict,
    job_description: Optional[str] = None,
) -> list:
    """
    Generate a sorted list of recommendation dicts based on dimension scores.

    Only generates recommendations for dimensions that need improvement.
    Sorted by priority: high → medium → low.
    """
    recs = []

    contact_score = scores.get("contact", 100)
    structure_score = scores.get("structure", 100)
    formatting_score = scores.get("formatting", 100)
    keyword_score = scores.get("keywords", 100)
    skills_score = scores.get("skills", 100)
    projects_score = scores.get("projects", 100)
    experience_score = scores.get("experience", 100)
    education_score = scores.get("education", 100)
    job_score = scores.get("job_alignment", 100)

    if contact_score < 90:
        recs.extend(_contact_recs(contact_score, analysis_data.get("contact", {})))
    if structure_score < 90:
        recs.extend(_structure_recs(structure_score, analysis_data.get("structure", {})))
    if formatting_score < 80:
        recs.extend(_formatting_recs(formatting_score, analysis_data.get("formatting", {})))
    if keyword_score < 70:
        recs.extend(_keyword_recs(keyword_score, analysis_data.get("keywords", {})))
    if skills_score < 70:
        recs.extend(_skills_recs(skills_score, analysis_data.get("skills", {})))
    if projects_score < 80:
        recs.extend(_projects_recs(projects_score, analysis_data.get("projects", {})))
    if experience_score < 70:
        recs.extend(_experience_recs(experience_score, analysis_data.get("experience", {})))
    if education_score < 70:
        recs.extend(_education_recs(education_score, analysis_data.get("education", {})))
    if job_score < 80:
        recs.extend(_job_alignment_recs(job_score, analysis_data.get("job_alignment", {}), job_description))

    # Sort: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 3))

    return recs
