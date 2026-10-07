"""
Demo job provider — always available, never real listings.
30 realistic demo jobs clearly labeled with is_demo=True.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from app.jobs.providers.base import JobProvider, JobData
from app.models.jobs import JobTypeEnum, WorkModeEnum

_now = datetime.utcnow()


DEMO_JOBS: List[dict] = [
    # ── Software Engineering ─────────────────────────────────────────────────
    {
        "external_id": "demo-001",
        "title": "Software Engineer",
        "company": "TechCorp India",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 800000,
        "salary_max": 1500000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 3.0,
        "required_skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Git"],
        "description": (
            "We are looking for a motivated Software Engineer to join our growing team. "
            "You will design, develop, and maintain scalable backend services. "
            "Strong knowledge of Python and Django required. Experience with cloud platforms a plus."
        ),
        "application_url": "https://example.com/jobs/demo-001",
        "days_ago": 2,
    },
    {
        "external_id": "demo-002",
        "title": "Frontend Developer",
        "company": "Webify Solutions",
        "location": "Mumbai, Maharashtra, India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 600000,
        "salary_max": 1200000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["React", "JavaScript", "TypeScript", "CSS", "HTML", "TailwindCSS"],
        "description": (
            "Join our frontend team to build beautiful and performant web applications. "
            "You will work closely with designers and backend engineers. "
            "Proficiency in React and TypeScript is required."
        ),
        "application_url": "https://example.com/jobs/demo-002",
        "days_ago": 5,
    },
    {
        "external_id": "demo-003",
        "title": "Full Stack Developer",
        "company": "StartupNest",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 900000,
        "salary_max": 1800000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["React", "Node.js", "MongoDB", "Express", "TypeScript", "Docker"],
        "description": (
            "Build end-to-end features across our SaaS platform. "
            "You will own features from conception to production. "
            "Remote-first culture, async communication."
        ),
        "application_url": "https://example.com/jobs/demo-003",
        "days_ago": 1,
    },
    {
        "external_id": "demo-004",
        "title": "Backend Developer",
        "company": "FinEdge Technologies",
        "location": "Hyderabad, Telangana, India",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1000000,
        "salary_max": 2000000,
        "salary_currency": "INR",
        "experience_min_years": 3.0,
        "experience_max_years": 6.0,
        "required_skills": ["Java", "Spring Boot", "Microservices", "Kafka", "PostgreSQL", "AWS"],
        "description": (
            "Design and implement high-performance backend services for our fintech platform. "
            "Strong Java and microservices experience required. "
            "Knowledge of event-driven architectures preferred."
        ),
        "application_url": "https://example.com/jobs/demo-004",
        "days_ago": 3,
    },
    # ── Data / Analytics ─────────────────────────────────────────────────────
    {
        "external_id": "demo-005",
        "title": "Data Analyst",
        "company": "Insight Analytics",
        "location": "Chennai, Tamil Nadu, India",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 500000,
        "salary_max": 1000000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 2.0,
        "required_skills": ["SQL", "Excel", "Python", "Tableau", "Data Visualization"],
        "description": (
            "Analyze large datasets to generate actionable insights for business stakeholders. "
            "Build dashboards and reports. Strong SQL and visualization skills required."
        ),
        "application_url": "https://example.com/jobs/demo-005",
        "days_ago": 7,
    },
    {
        "external_id": "demo-006",
        "title": "Data Engineer",
        "company": "DataFlow Inc.",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1200000,
        "salary_max": 2200000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Python", "Apache Spark", "Hadoop", "SQL", "AWS", "Airflow"],
        "description": (
            "Build and maintain robust data pipelines. "
            "Experience with distributed computing frameworks required. "
            "Familiarity with cloud data services (AWS Glue, S3, Redshift) preferred."
        ),
        "application_url": "https://example.com/jobs/demo-006",
        "days_ago": 4,
    },
    {
        "external_id": "demo-007",
        "title": "Business Intelligence Developer",
        "company": "RetailMax",
        "location": "Delhi, India",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 700000,
        "salary_max": 1400000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["Power BI", "SQL", "DAX", "Excel", "Data Modeling"],
        "description": (
            "Develop and maintain BI dashboards using Power BI. "
            "Work with business teams to gather requirements and deliver insights. "
            "Strong SQL and data modeling skills required."
        ),
        "application_url": "https://example.com/jobs/demo-007",
        "days_ago": 6,
    },
    # ── Machine Learning / AI ─────────────────────────────────────────────────
    {
        "external_id": "demo-008",
        "title": "Machine Learning Engineer",
        "company": "AI Ventures",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1500000,
        "salary_max": 3000000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLOps", "Docker"],
        "description": (
            "Build and deploy machine learning models at scale. "
            "Work on NLP, computer vision, and recommendation systems. "
            "Strong Python and deep learning framework knowledge required."
        ),
        "application_url": "https://example.com/jobs/demo-008",
        "days_ago": 2,
    },
    {
        "external_id": "demo-009",
        "title": "Data Scientist",
        "company": "HealthAI Solutions",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 1200000,
        "salary_max": 2500000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 6.0,
        "required_skills": ["Python", "R", "Machine Learning", "Statistics", "Pandas", "Scikit-learn"],
        "description": (
            "Apply statistical models and ML techniques to healthcare data. "
            "Collaborate with clinicians and engineers to deliver data-driven solutions. "
            "Strong statistics and Python required."
        ),
        "application_url": "https://example.com/jobs/demo-009",
        "days_ago": 10,
    },
    {
        "external_id": "demo-010",
        "title": "NLP Engineer",
        "company": "LangTech",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 1800000,
        "salary_max": 3500000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Python", "NLP", "Transformers", "BERT", "PyTorch", "Hugging Face"],
        "description": (
            "Build state-of-the-art NLP pipelines for text classification, NER, and generation. "
            "Work with large language models. "
            "Proficiency in HuggingFace and PyTorch required."
        ),
        "application_url": "https://example.com/jobs/demo-010",
        "days_ago": 8,
    },
    # ── DevOps / Cloud ────────────────────────────────────────────────────────
    {
        "external_id": "demo-011",
        "title": "DevOps Engineer",
        "company": "CloudBase Systems",
        "location": "Hyderabad, Telangana, India",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1000000,
        "salary_max": 2000000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux"],
        "description": (
            "Automate and maintain infrastructure for cloud-native applications. "
            "Manage CI/CD pipelines, containerized workloads, and cloud resources. "
            "AWS and Kubernetes experience required."
        ),
        "application_url": "https://example.com/jobs/demo-011",
        "days_ago": 3,
    },
    {
        "external_id": "demo-012",
        "title": "Site Reliability Engineer",
        "company": "ScaleUp Technologies",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1500000,
        "salary_max": 2800000,
        "salary_currency": "INR",
        "experience_min_years": 3.0,
        "experience_max_years": 7.0,
        "required_skills": ["Linux", "Python", "Kubernetes", "Prometheus", "Grafana", "Incident Management"],
        "description": (
            "Ensure reliability and availability of production systems. "
            "Develop automation tools and manage incident response. "
            "Strong Linux and Python skills required."
        ),
        "application_url": "https://example.com/jobs/demo-012",
        "days_ago": 5,
    },
    {
        "external_id": "demo-013",
        "title": "Cloud Architect",
        "company": "EnterpriseCloud",
        "location": "Mumbai, Maharashtra, India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 2500000,
        "salary_max": 4500000,
        "salary_currency": "INR",
        "experience_min_years": 5.0,
        "experience_max_years": 10.0,
        "required_skills": ["AWS", "Azure", "GCP", "Terraform", "Architecture Design", "Security"],
        "description": (
            "Design cloud architectures for enterprise clients. "
            "Lead cloud migration and modernization initiatives. "
            "Multi-cloud experience required."
        ),
        "application_url": "https://example.com/jobs/demo-013",
        "days_ago": 12,
    },
    # ── Mobile ────────────────────────────────────────────────────────────────
    {
        "external_id": "demo-014",
        "title": "Android Developer",
        "company": "AppFactory",
        "location": "Delhi, India",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 700000,
        "salary_max": 1400000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["Kotlin", "Android SDK", "MVVM", "Retrofit", "Jetpack Compose"],
        "description": (
            "Build and maintain Android applications for millions of users. "
            "Work with cross-functional teams on new features. "
            "Kotlin and Jetpack Compose experience required."
        ),
        "application_url": "https://example.com/jobs/demo-014",
        "days_ago": 9,
    },
    {
        "external_id": "demo-015",
        "title": "iOS Developer",
        "company": "AppFactory",
        "location": "Delhi, India",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 700000,
        "salary_max": 1400000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["Swift", "Xcode", "UIKit", "SwiftUI", "Core Data"],
        "description": (
            "Build and ship iOS apps with a focus on performance and user experience. "
            "Swift and SwiftUI required. "
            "Experience with CI/CD for iOS apps is a plus."
        ),
        "application_url": "https://example.com/jobs/demo-015",
        "days_ago": 9,
    },
    {
        "external_id": "demo-016",
        "title": "Flutter Developer",
        "company": "CrossPlatform Labs",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 800000,
        "salary_max": 1600000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 3.0,
        "required_skills": ["Flutter", "Dart", "Firebase", "REST APIs", "State Management"],
        "description": (
            "Build cross-platform mobile apps using Flutter. "
            "Work on both Android and iOS deliverables from a single codebase. "
            "Flutter and Dart proficiency required."
        ),
        "application_url": "https://example.com/jobs/demo-016",
        "days_ago": 4,
    },
    # ── QA / Testing ─────────────────────────────────────────────────────────
    {
        "external_id": "demo-017",
        "title": "QA Engineer",
        "company": "QualityFirst",
        "location": "Chennai, Tamil Nadu, India",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 500000,
        "salary_max": 1000000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 3.0,
        "required_skills": ["Selenium", "Python", "TestNG", "API Testing", "Postman", "JIRA"],
        "description": (
            "Develop and execute automated test suites to ensure product quality. "
            "Collaborate with developers to identify and resolve defects. "
            "Selenium and Python automation experience required."
        ),
        "application_url": "https://example.com/jobs/demo-017",
        "days_ago": 6,
    },
    {
        "external_id": "demo-018",
        "title": "SDET (Software Development Engineer in Test)",
        "company": "TestPro Systems",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 900000,
        "salary_max": 1800000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Java", "Selenium", "TestNG", "CI/CD", "API Testing", "Performance Testing"],
        "description": (
            "Build test frameworks and contribute to product quality at scale. "
            "Java-based test automation expertise required. "
            "Experience with performance testing tools a plus."
        ),
        "application_url": "https://example.com/jobs/demo-018",
        "days_ago": 11,
    },
    # ── Internships ───────────────────────────────────────────────────────────
    {
        "external_id": "demo-019",
        "title": "Software Engineering Intern",
        "company": "InnovateTech",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.internship,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 20000,
        "salary_max": 50000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 0.0,
        "required_skills": ["Python", "Data Structures", "Algorithms", "Git"],
        "description": (
            "6-month internship for final-year B.Tech students. "
            "Work on real product features under senior engineer mentorship. "
            "Strong DSA skills required."
        ),
        "application_url": "https://example.com/jobs/demo-019",
        "days_ago": 1,
    },
    {
        "external_id": "demo-020",
        "title": "Data Science Intern",
        "company": "DataMinds",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.internship,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 15000,
        "salary_max": 30000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 0.0,
        "required_skills": ["Python", "Pandas", "Scikit-learn", "Statistics", "Jupyter"],
        "description": (
            "3-month remote internship. "
            "Work on real ML projects and publish results. "
            "Ideal for students interested in data science careers."
        ),
        "application_url": "https://example.com/jobs/demo-020",
        "days_ago": 0,
    },
    {
        "external_id": "demo-021",
        "title": "Frontend Development Intern",
        "company": "PixelCraft Studio",
        "location": "Mumbai, Maharashtra, India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "job_type": JobTypeEnum.internship,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 15000,
        "salary_max": 25000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 0.0,
        "required_skills": ["React", "JavaScript", "HTML", "CSS"],
        "description": (
            "4-month internship building UI components for consumer-facing products. "
            "Good knowledge of React and modern JS required."
        ),
        "application_url": "https://example.com/jobs/demo-021",
        "days_ago": 2,
    },
    {
        "external_id": "demo-022",
        "title": "DevOps Intern",
        "company": "CloudOps India",
        "location": "Hyderabad, Telangana, India",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "job_type": JobTypeEnum.internship,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 20000,
        "salary_max": 30000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 0.0,
        "required_skills": ["Linux", "Docker", "Git", "Shell Scripting", "AWS"],
        "description": (
            "Assist the DevOps team with infrastructure automation and monitoring. "
            "Linux and Docker basics required."
        ),
        "application_url": "https://example.com/jobs/demo-022",
        "days_ago": 3,
    },
    # ── Security / Architecture ────────────────────────────────────────────────
    {
        "external_id": "demo-023",
        "title": "Cybersecurity Analyst",
        "company": "SecureNet India",
        "location": "Delhi, India",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 900000,
        "salary_max": 1800000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 5.0,
        "required_skills": ["Network Security", "SIEM", "Penetration Testing", "Python", "CEH"],
        "description": (
            "Monitor security events, investigate threats, and respond to incidents. "
            "CEH or CISSP certification preferred. "
            "Strong knowledge of network security and SIEM tools required."
        ),
        "application_url": "https://example.com/jobs/demo-023",
        "days_ago": 14,
    },
    {
        "external_id": "demo-024",
        "title": "Solutions Architect",
        "company": "Enterprise Systems Ltd.",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 3000000,
        "salary_max": 5500000,
        "salary_currency": "INR",
        "experience_min_years": 8.0,
        "experience_max_years": 15.0,
        "required_skills": ["AWS", "System Design", "Microservices", "Java", "Architecture Patterns"],
        "description": (
            "Lead architecture design for large-scale enterprise solutions. "
            "Interact with CXO-level stakeholders. "
            "Extensive AWS and system design experience required."
        ),
        "application_url": "https://example.com/jobs/demo-024",
        "days_ago": 7,
    },
    # ── Product / Management ──────────────────────────────────────────────────
    {
        "external_id": "demo-025",
        "title": "Product Manager",
        "company": "ProductLabs",
        "location": "Bangalore, Karnataka, India",
        "city": "Bangalore",
        "state": "Karnataka",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.hybrid,
        "salary_min": 1800000,
        "salary_max": 3500000,
        "salary_currency": "INR",
        "experience_min_years": 3.0,
        "experience_max_years": 7.0,
        "required_skills": ["Product Strategy", "Agile", "JIRA", "Data Analysis", "User Research", "Roadmapping"],
        "description": (
            "Define and drive the product roadmap for our B2B SaaS platform. "
            "Work with engineering, design, and sales teams. "
            "Strong analytical and communication skills required."
        ),
        "application_url": "https://example.com/jobs/demo-025",
        "days_ago": 4,
    },
    {
        "external_id": "demo-026",
        "title": "Scrum Master",
        "company": "AgileWorks",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.contract,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 1000000,
        "salary_max": 2000000,
        "salary_currency": "INR",
        "experience_min_years": 2.0,
        "experience_max_years": 6.0,
        "required_skills": ["Scrum", "Agile", "JIRA", "Facilitation", "CSM Certification"],
        "description": (
            "Facilitate scrum ceremonies and remove team impediments. "
            "Coach teams on Agile best practices. "
            "CSM certification required."
        ),
        "application_url": "https://example.com/jobs/demo-026",
        "days_ago": 8,
    },
    # ── Design / UX ───────────────────────────────────────────────────────────
    {
        "external_id": "demo-027",
        "title": "UI/UX Designer",
        "company": "DesignFirst Agency",
        "location": "Mumbai, Maharashtra, India",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 600000,
        "salary_max": 1200000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["Figma", "Adobe XD", "User Research", "Prototyping", "Wireframing"],
        "description": (
            "Create intuitive UI/UX designs for web and mobile products. "
            "Conduct user research and usability testing. "
            "Proficiency in Figma required."
        ),
        "application_url": "https://example.com/jobs/demo-027",
        "days_ago": 6,
    },
    # ── Part-time / Freelance ─────────────────────────────────────────────────
    {
        "external_id": "demo-028",
        "title": "Python Developer",
        "company": "FreelanceHub",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.freelance,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 500000,
        "salary_max": 1000000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 5.0,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Celery"],
        "description": (
            "Short-term freelance project (3-6 months). "
            "Build REST API backend for a logistics platform. "
            "Python and FastAPI expertise required."
        ),
        "application_url": "https://example.com/jobs/demo-028",
        "days_ago": 2,
    },
    {
        "external_id": "demo-029",
        "title": "Technical Content Writer",
        "company": "TechPublish",
        "location": "Remote",
        "city": "",
        "state": "",
        "country": "India",
        "job_type": JobTypeEnum.part_time,
        "work_mode": WorkModeEnum.remote,
        "salary_min": 200000,
        "salary_max": 500000,
        "salary_currency": "INR",
        "experience_min_years": 0.0,
        "experience_max_years": 2.0,
        "required_skills": ["Technical Writing", "Python", "Git", "Markdown", "Documentation"],
        "description": (
            "Write technical blog posts, tutorials, and documentation for developers. "
            "Part-time, remote. "
            "Programming knowledge and writing skills required."
        ),
        "application_url": "https://example.com/jobs/demo-029",
        "days_ago": 13,
    },
    {
        "external_id": "demo-030",
        "title": "Embedded Systems Engineer",
        "company": "IoTech Labs",
        "location": "Pune, Maharashtra, India",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "job_type": JobTypeEnum.full_time,
        "work_mode": WorkModeEnum.on_site,
        "salary_min": 800000,
        "salary_max": 1600000,
        "salary_currency": "INR",
        "experience_min_years": 1.0,
        "experience_max_years": 4.0,
        "required_skills": ["C", "C++", "RTOS", "Embedded Linux", "IoT", "Microcontrollers"],
        "description": (
            "Develop firmware and embedded software for IoT devices. "
            "Strong C/C++ and RTOS experience required. "
            "Knowledge of communication protocols (MQTT, Modbus) preferred."
        ),
        "application_url": "https://example.com/jobs/demo-030",
        "days_ago": 5,
    },
]


def _build_job_data(raw: dict) -> JobData:
    posted = _now - timedelta(days=raw.get("days_ago", 0))
    return JobData(
        external_id=raw["external_id"],
        title=raw["title"],
        company=raw["company"],
        location=raw["location"],
        city=raw.get("city", ""),
        state=raw.get("state", ""),
        country=raw.get("country", ""),
        job_type=raw.get("job_type"),
        work_mode=raw.get("work_mode"),
        salary_min=raw.get("salary_min"),
        salary_max=raw.get("salary_max"),
        salary_currency=raw.get("salary_currency", "INR"),
        experience_min_years=raw.get("experience_min_years"),
        experience_max_years=raw.get("experience_max_years"),
        required_skills=raw.get("required_skills", []),
        description=raw.get("description", ""),
        application_url=raw.get("application_url", ""),
        source_url=raw.get("application_url", ""),
        posted_date=posted,
        is_demo=True,
        source_slug="demo",
    )


class DemoProvider(JobProvider):
    """Returns demo job listings. Always available, never real."""

    slug = "demo"

    def is_available(self) -> bool:
        return True

    def fetch_jobs(
        self,
        keywords: str = "",
        location: str = "",
        job_type: Optional[str] = None,
        work_mode: Optional[str] = None,
        limit: int = 20,
    ) -> List[JobData]:
        jobs = [_build_job_data(r) for r in DEMO_JOBS]

        # Filter by keywords
        if keywords:
            kw = keywords.lower()
            jobs = [
                j for j in jobs
                if kw in j.title.lower()
                or kw in j.company.lower()
                or any(kw in s.lower() for s in j.required_skills)
                or kw in j.description.lower()
            ]

        # Filter by location
        if location and location.lower() not in ("anywhere", "remote", "worldwide"):
            loc = location.lower()
            filtered = [
                j for j in jobs
                if loc in (j.location or "").lower()
                or loc in (j.city or "").lower()
                or (j.work_mode == WorkModeEnum.remote)
            ]
            # Fall back to all if filter is too strict
            jobs = filtered if filtered else jobs

        # Filter by job_type
        if job_type:
            try:
                jt = JobTypeEnum(job_type)
                jobs = [j for j in jobs if j.job_type == jt]
            except ValueError:
                pass

        # Filter by work_mode
        if work_mode:
            try:
                wm = WorkModeEnum(work_mode)
                jobs = [j for j in jobs if j.work_mode == wm]
            except ValueError:
                pass

        return jobs[:limit]

    def get_job_detail(self, job_id: str) -> Optional[JobData]:
        for raw in DEMO_JOBS:
            if raw["external_id"] == job_id:
                return _build_job_data(raw)
        return None
