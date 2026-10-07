"""
Curated learning resources database.

All URLs are real, publicly accessible resources from authoritative providers.
Resources are keyed by normalized skill name.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional


# ── Curated resource database ─────────────────────────────────────────────────
# Format per resource:
#   skill_name, resource_name, provider, url, topics, difficulty, is_free,
#   duration_hours, description, why_recommended

RESOURCES: List[Dict[str, Any]] = [
    # ── Python ───────────────────────────────────────────────────────────────
    {
        "skill_name": "python",
        "resource_name": "Python for Everybody Specialization",
        "provider": "Coursera / University of Michigan",
        "url": "https://www.coursera.org/specializations/python",
        "topics": ["syntax", "data structures", "web scraping", "databases", "data visualization"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 32,
        "description": "Comprehensive introduction to Python programming from one of the most popular instructors.",
        "why_recommended": "One of the highest-rated Python courses; audit for free; covers everything from basics to databases.",
    },
    {
        "skill_name": "python",
        "resource_name": "The Python Tutorial",
        "provider": "Python.org (Official Docs)",
        "url": "https://docs.python.org/3/tutorial/",
        "topics": ["syntax", "modules", "classes", "exceptions", "stdlib"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 10,
        "description": "The official Python tutorial covering core language features.",
        "why_recommended": "Authoritative source directly from the Python maintainers — always up to date.",
    },
    {
        "skill_name": "python",
        "resource_name": "Python Crash Course on freeCodeCamp",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/news/the-python-guide-for-beginners/",
        "topics": ["syntax", "functions", "OOP", "file I/O"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 8,
        "description": "Free beginner guide to Python with hands-on practice.",
        "why_recommended": "Completely free, project-based, great for beginners.",
    },
    # ── JavaScript ───────────────────────────────────────────────────────────
    {
        "skill_name": "javascript",
        "resource_name": "JavaScript Algorithms and Data Structures",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
        "topics": ["ES6", "regular expressions", "debugging", "OOP", "functional programming"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 300,
        "description": "Full JavaScript curriculum with interactive coding challenges and certification.",
        "why_recommended": "Completely free certification with hundreds of interactive exercises.",
    },
    {
        "skill_name": "javascript",
        "resource_name": "The Modern JavaScript Tutorial",
        "provider": "javascript.info",
        "url": "https://javascript.info/",
        "topics": ["closures", "promises", "async/await", "DOM", "classes", "modules"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 40,
        "description": "Comprehensive, modern guide to JavaScript from fundamentals to advanced topics.",
        "why_recommended": "Best free JavaScript reference — up to date with modern JS (ES2020+).",
    },
    # ── TypeScript ───────────────────────────────────────────────────────────
    {
        "skill_name": "typescript",
        "resource_name": "TypeScript Handbook",
        "provider": "TypeScript Official Docs",
        "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
        "topics": ["types", "interfaces", "generics", "enums", "decorators"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 12,
        "description": "Official TypeScript handbook from Microsoft.",
        "why_recommended": "Authoritative and free — directly from the TypeScript team.",
    },
    # ── React ────────────────────────────────────────────────────────────────
    {
        "skill_name": "react",
        "resource_name": "React Official Documentation",
        "provider": "React.dev (Meta)",
        "url": "https://react.dev/learn",
        "topics": ["components", "hooks", "state management", "effects", "context"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 15,
        "description": "The new official React docs with interactive examples and tutorials.",
        "why_recommended": "Best place to learn React — interactive, modern, maintained by the React team.",
    },
    {
        "skill_name": "react",
        "resource_name": "Full Stack Open – Part 1 & 2 (React)",
        "provider": "University of Helsinki",
        "url": "https://fullstackopen.com/en/",
        "topics": ["hooks", "state", "forms", "REST", "testing"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 60,
        "description": "Free full stack university course covering React, Node.js, MongoDB and more.",
        "why_recommended": "University-quality free course with real projects.",
    },
    # ── SQL ──────────────────────────────────────────────────────────────────
    {
        "skill_name": "sql",
        "resource_name": "SQL Tutorial",
        "provider": "W3Schools",
        "url": "https://www.w3schools.com/sql/",
        "topics": ["SELECT", "JOINs", "GROUP BY", "subqueries", "indexes"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 6,
        "description": "Interactive SQL tutorial with try-it-yourself exercises.",
        "why_recommended": "Quick, free, interactive reference for SQL essentials.",
    },
    {
        "skill_name": "sql",
        "resource_name": "Databases and SQL for Data Science with Python",
        "provider": "Coursera / IBM",
        "url": "https://www.coursera.org/learn/sql-data-science",
        "topics": ["SELECT", "JOINs", "aggregation", "subqueries", "Python integration"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 20,
        "description": "IBM's free SQL course (audit mode) focused on data science use cases.",
        "why_recommended": "IBM-backed, free to audit, practical focus with Python integration.",
    },
    # ── Machine Learning ─────────────────────────────────────────────────────
    {
        "skill_name": "machine learning",
        "resource_name": "Machine Learning Specialization",
        "provider": "Coursera / Andrew Ng (Stanford + DeepLearning.AI)",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "topics": ["supervised learning", "unsupervised learning", "neural networks", "recommender systems"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 90,
        "description": "The gold-standard ML course by Andrew Ng, fully updated for 2024.",
        "why_recommended": "Best-in-class ML fundamentals course, audit for free.",
    },
    {
        "skill_name": "machine learning",
        "resource_name": "Intro to Machine Learning",
        "provider": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "topics": ["decision trees", "random forests", "validation", "underfitting/overfitting"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 3,
        "description": "Hands-on ML mini-course with real datasets on Kaggle.",
        "why_recommended": "Completely free, hands-on with real data, earns a Kaggle certificate.",
    },
    # ── Deep Learning ────────────────────────────────────────────────────────
    {
        "skill_name": "deep learning",
        "resource_name": "Deep Learning Specialization",
        "provider": "Coursera / DeepLearning.AI",
        "url": "https://www.coursera.org/specializations/deep-learning",
        "topics": ["neural networks", "CNN", "RNN", "LSTM", "hyperparameter tuning", "batch norm"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 120,
        "description": "Five-course specialization by Andrew Ng covering all aspects of deep learning.",
        "why_recommended": "The definitive deep learning curriculum — audit for free.",
    },
    {
        "skill_name": "deep learning",
        "resource_name": "Practical Deep Learning for Coders",
        "provider": "fast.ai",
        "url": "https://course.fast.ai/",
        "topics": ["image classification", "NLP", "tabular data", "deployment", "diffusion models"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 30,
        "description": "Top-down deep learning course using PyTorch — practical and free.",
        "why_recommended": "Free, practical, and project-first approach using modern PyTorch.",
    },
    # ── TensorFlow / PyTorch ─────────────────────────────────────────────────
    {
        "skill_name": "tensorflow",
        "resource_name": "TensorFlow Tutorials",
        "provider": "TensorFlow Official",
        "url": "https://www.tensorflow.org/tutorials",
        "topics": ["Keras", "training", "deployment", "TensorFlow Lite", "TensorBoard"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 20,
        "description": "Official TensorFlow tutorials from beginner to advanced.",
        "why_recommended": "Authoritative, free, directly from the TensorFlow team.",
    },
    {
        "skill_name": "pytorch",
        "resource_name": "PyTorch Tutorials",
        "provider": "PyTorch Official",
        "url": "https://pytorch.org/tutorials/",
        "topics": ["tensors", "autograd", "neural networks", "CUDA", "deployment"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 20,
        "description": "Official PyTorch tutorials covering all major use cases.",
        "why_recommended": "Free and authoritative — directly from Meta's PyTorch team.",
    },
    # ── scikit-learn ─────────────────────────────────────────────────────────
    {
        "skill_name": "scikit-learn",
        "resource_name": "scikit-learn User Guide",
        "provider": "scikit-learn (Official Docs)",
        "url": "https://scikit-learn.org/stable/user_guide.html",
        "topics": ["classification", "regression", "clustering", "preprocessing", "pipelines"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 10,
        "description": "Comprehensive official guide to scikit-learn.",
        "why_recommended": "The only reference you need — always up to date and free.",
    },
    # ── Pandas ───────────────────────────────────────────────────────────────
    {
        "skill_name": "pandas",
        "resource_name": "Pandas Tutorial",
        "provider": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn/pandas",
        "topics": ["DataFrames", "indexing", "groupby", "merging", "time series"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 4,
        "description": "Hands-on pandas course on Kaggle with real datasets.",
        "why_recommended": "Free, fast, and earns a Kaggle certificate.",
    },
    {
        "skill_name": "pandas",
        "resource_name": "Pandas User Guide",
        "provider": "pandas (Official Docs)",
        "url": "https://pandas.pydata.org/docs/user_guide/index.html",
        "topics": ["Series", "DataFrame", "IO tools", "indexing", "reshaping"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 8,
        "description": "Official pandas user guide — comprehensive reference.",
        "why_recommended": "Authoritative source maintained by the pandas core team.",
    },
    # ── Git ──────────────────────────────────────────────────────────────────
    {
        "skill_name": "git",
        "resource_name": "Introduction to Git and GitHub",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/learn/introduction-git-github",
        "topics": ["version control", "branches", "pull requests", "collaboration", "GitHub Actions"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 16,
        "description": "Google's free course on Git and GitHub fundamentals.",
        "why_recommended": "Free to audit, from Google, covers practical Git workflows.",
    },
    {
        "skill_name": "git",
        "resource_name": "Pro Git Book",
        "provider": "git-scm.com",
        "url": "https://git-scm.com/book/en/v2",
        "topics": ["branching", "merging", "rebasing", "internals", "advanced workflows"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 12,
        "description": "The complete, free Git reference book available online.",
        "why_recommended": "The definitive free Git book — from the Git official site.",
    },
    # ── Docker ───────────────────────────────────────────────────────────────
    {
        "skill_name": "docker",
        "resource_name": "Docker Get Started Tutorial",
        "provider": "Docker Official",
        "url": "https://docs.docker.com/get-started/",
        "topics": ["containers", "images", "Dockerfile", "docker-compose", "registries"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 5,
        "description": "Official Docker beginner tutorial from the Docker team.",
        "why_recommended": "Free, authoritative, hands-on intro to Docker.",
    },
    # ── Kubernetes ───────────────────────────────────────────────────────────
    {
        "skill_name": "kubernetes",
        "resource_name": "Kubernetes Documentation – Tutorials",
        "provider": "Kubernetes Official",
        "url": "https://kubernetes.io/docs/tutorials/",
        "topics": ["pods", "deployments", "services", "namespaces", "helm", "ingress"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 10,
        "description": "Official Kubernetes tutorials for learning cluster orchestration.",
        "why_recommended": "Free, authoritative, always current.",
    },
    {
        "skill_name": "kubernetes",
        "resource_name": "Introduction to Kubernetes",
        "provider": "IBM SkillsBuild / edX",
        "url": "https://www.edx.org/learn/kubernetes/the-linux-foundation-introduction-to-kubernetes",
        "topics": ["pods", "deployments", "ConfigMaps", "volumes", "stateful sets"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 30,
        "description": "Linux Foundation's free Introduction to Kubernetes course on edX.",
        "why_recommended": "Industry-recognized, free to audit from the Linux Foundation.",
    },
    # ── AWS ──────────────────────────────────────────────────────────────────
    {
        "skill_name": "aws",
        "resource_name": "AWS Cloud Practitioner Essentials",
        "provider": "AWS Skill Builder",
        "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
        "topics": ["AWS global infrastructure", "core services", "security", "pricing", "support"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 6,
        "description": "Free AWS foundational course covering all AWS core services.",
        "why_recommended": "Free from AWS — perfect for Cloud Practitioner certification prep.",
    },
    {
        "skill_name": "aws",
        "resource_name": "AWS Solutions Architect Learning Path",
        "provider": "AWS Skill Builder",
        "url": "https://explore.skillbuilder.aws/learn/public/learning_plan/view/1044/solutions-architect-learning-plan",
        "topics": ["EC2", "S3", "VPC", "Lambda", "RDS", "high availability"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 40,
        "description": "AWS's own structured learning path for Solutions Architect.",
        "why_recommended": "Directly from AWS, free, aligned with SAA-C03 certification.",
    },
    # ── Azure ────────────────────────────────────────────────────────────────
    {
        "skill_name": "azure",
        "resource_name": "Microsoft Azure Fundamentals (AZ-900)",
        "provider": "Microsoft Learn",
        "url": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/",
        "topics": ["cloud concepts", "Azure services", "security", "pricing", "SLAs"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 11,
        "description": "Free Microsoft AZ-900 learning path covering Azure fundamentals.",
        "why_recommended": "Free, from Microsoft, aligned with AZ-900 certification.",
    },
    # ── GCP ──────────────────────────────────────────────────────────────────
    {
        "skill_name": "gcp",
        "resource_name": "Google Cloud Fundamentals: Core Infrastructure",
        "provider": "Google Cloud Skills Boost",
        "url": "https://www.cloudskillsboost.google/course_templates/60",
        "topics": ["Compute Engine", "Cloud Storage", "Cloud SQL", "Kubernetes Engine", "IAM"],
        "difficulty": "beginner",
        "is_free": False,
        "duration_hours": 9,
        "description": "Google's core GCP infrastructure course (credits sometimes available).",
        "why_recommended": "Official Google curriculum — aligned with ACE certification.",
    },
    # ── Terraform ────────────────────────────────────────────────────────────
    {
        "skill_name": "terraform",
        "resource_name": "Terraform Tutorials",
        "provider": "HashiCorp (Official)",
        "url": "https://developer.hashicorp.com/terraform/tutorials",
        "topics": ["providers", "resources", "state", "modules", "workspaces"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 15,
        "description": "Official HashiCorp Terraform tutorials with hands-on labs.",
        "why_recommended": "Free, from the creators of Terraform, hands-on labs.",
    },
    # ── Data Visualization ───────────────────────────────────────────────────
    {
        "skill_name": "data visualization",
        "resource_name": "Data Visualization",
        "provider": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn/data-visualization",
        "topics": ["seaborn", "matplotlib", "line charts", "bar charts", "heatmaps", "pair plots"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 4,
        "description": "Free Kaggle mini-course on data visualization with Python.",
        "why_recommended": "Free, hands-on, earns a Kaggle certificate.",
    },
    # ── Statistics ───────────────────────────────────────────────────────────
    {
        "skill_name": "statistics",
        "resource_name": "Statistics with Python Specialization",
        "provider": "Coursera / University of Michigan",
        "url": "https://www.coursera.org/specializations/statistics-with-python",
        "topics": ["descriptive stats", "probability", "inference", "hypothesis testing", "regression"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 60,
        "description": "Three-course statistics specialization using Python — audit for free.",
        "why_recommended": "University-quality statistics course, free to audit.",
    },
    # ── Linux ────────────────────────────────────────────────────────────────
    {
        "skill_name": "linux",
        "resource_name": "Introduction to Linux",
        "provider": "The Linux Foundation / edX",
        "url": "https://www.edx.org/learn/linux/the-linux-foundation-introduction-to-linux",
        "topics": ["shell", "file system", "processes", "networking", "security"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 60,
        "description": "Linux Foundation's free Introduction to Linux course on edX.",
        "why_recommended": "Free, from the Linux Foundation — the definitive beginner course.",
    },
    # ── Networking ───────────────────────────────────────────────────────────
    {
        "skill_name": "networking",
        "resource_name": "The Bits and Bytes of Computer Networking",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/learn/computer-networking",
        "topics": ["TCP/IP", "DNS", "DHCP", "firewalls", "protocols", "troubleshooting"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 30,
        "description": "Google IT Support certificate networking course — audit for free.",
        "why_recommended": "Free to audit, from Google, excellent coverage of networking fundamentals.",
    },
    # ── CI/CD ────────────────────────────────────────────────────────────────
    {
        "skill_name": "ci/cd",
        "resource_name": "GitHub Actions Documentation",
        "provider": "GitHub Official",
        "url": "https://docs.github.com/en/actions",
        "topics": ["workflows", "jobs", "actions", "secrets", "matrix builds", "deployment"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 8,
        "description": "Official GitHub Actions documentation with quickstarts and guides.",
        "why_recommended": "Free, authoritative, GitHub Actions is the most-used CI/CD platform.",
    },
    # ── REST API ─────────────────────────────────────────────────────────────
    {
        "skill_name": "rest api",
        "resource_name": "APIs and Microservices Certification",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
        "topics": ["REST", "JSON", "Node.js", "Express", "MongoDB"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 300,
        "description": "freeCodeCamp's back-end development certification with REST API projects.",
        "why_recommended": "Completely free, project-based, earns a certification.",
    },
    # ── HTML & CSS ───────────────────────────────────────────────────────────
    {
        "skill_name": "html",
        "resource_name": "Responsive Web Design Certification",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        "topics": ["HTML5", "CSS3", "Flexbox", "Grid", "accessibility", "responsive design"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 300,
        "description": "Complete HTML and CSS curriculum with certification from freeCodeCamp.",
        "why_recommended": "Completely free certification with real project portfolio.",
    },
    {
        "skill_name": "css",
        "resource_name": "Responsive Web Design Certification",
        "provider": "freeCodeCamp",
        "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        "topics": ["CSS3", "Flexbox", "Grid", "animations", "variables", "responsive design"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 300,
        "description": "Complete HTML and CSS curriculum with certification.",
        "why_recommended": "Free, comprehensive, project-based CSS learning.",
    },
    # ── Figma ────────────────────────────────────────────────────────────────
    {
        "skill_name": "figma",
        "resource_name": "Figma for Beginners Tutorial",
        "provider": "Figma Official",
        "url": "https://help.figma.com/hc/en-us/sections/4405269443991-Figma-for-Beginners",
        "topics": ["frames", "components", "auto layout", "prototyping", "design tokens"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 4,
        "description": "Official Figma beginner tutorial series from the Figma team.",
        "why_recommended": "Free, from Figma themselves, quick and practical.",
    },
    # ── Cybersecurity ────────────────────────────────────────────────────────
    {
        "skill_name": "security monitoring",
        "resource_name": "Google Cybersecurity Professional Certificate",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "topics": ["SIEM", "incident response", "Python automation", "Linux", "network security"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 180,
        "description": "Google's comprehensive cybersecurity career certificate — audit for free.",
        "why_recommended": "From Google, free to audit, covers core SOC analyst skills.",
    },
    {
        "skill_name": "penetration testing",
        "resource_name": "Ethical Hacking – Beginner to Advanced",
        "provider": "IBM SkillsBuild",
        "url": "https://skillsbuild.org/adult-learners/digital-credentials/cybersecurity",
        "topics": ["reconnaissance", "scanning", "exploitation", "privilege escalation", "reporting"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 20,
        "description": "IBM SkillsBuild cybersecurity path covering ethical hacking concepts.",
        "why_recommended": "Free IBM credential, comprehensive ethical hacking coverage.",
    },
    # ── NLP ──────────────────────────────────────────────────────────────────
    {
        "skill_name": "nlp",
        "resource_name": "Natural Language Processing Specialization",
        "provider": "Coursera / DeepLearning.AI",
        "url": "https://www.coursera.org/specializations/natural-language-processing",
        "topics": ["classification", "word embeddings", "sequence models", "attention", "transformers"],
        "difficulty": "advanced",
        "is_free": True,
        "duration_hours": 120,
        "description": "Four-course NLP specialization by DeepLearning.AI — audit for free.",
        "why_recommended": "Comprehensive NLP from basics to transformers, free to audit.",
    },
    # ── Prompt Engineering / LLMs ────────────────────────────────────────────
    {
        "skill_name": "prompt engineering",
        "resource_name": "Prompt Engineering for Developers",
        "provider": "DeepLearning.AI (Short Course)",
        "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/",
        "topics": ["prompting principles", "iterative refinement", "summarizing", "inferring", "transforming"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 1,
        "description": "Free 1-hour course by DeepLearning.AI and OpenAI on prompt engineering.",
        "why_recommended": "Free, short, authoritative — co-created by OpenAI.",
    },
    {
        "skill_name": "llm",
        "resource_name": "LangChain for LLM Application Development",
        "provider": "DeepLearning.AI (Short Course)",
        "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/",
        "topics": ["chains", "memory", "agents", "tools", "RAG"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 1,
        "description": "Free short course on building LLM applications with LangChain.",
        "why_recommended": "Free, practical, with Harrison Chase (LangChain creator).",
    },
    # ── Cloud Architecture ───────────────────────────────────────────────────
    {
        "skill_name": "cloud architecture",
        "resource_name": "AWS Architecture Center",
        "provider": "Amazon Web Services",
        "url": "https://aws.amazon.com/architecture/",
        "topics": ["well-architected", "reference architectures", "microservices", "serverless"],
        "difficulty": "advanced",
        "is_free": True,
        "duration_hours": 20,
        "description": "AWS Architecture Center with whitepapers, reference architectures, and best practices.",
        "why_recommended": "Free resource from AWS covering real-world architecture patterns.",
    },
    # ── Product Strategy ─────────────────────────────────────────────────────
    {
        "skill_name": "product strategy",
        "resource_name": "Digital Product Management Specialization",
        "provider": "Coursera / University of Virginia",
        "url": "https://www.coursera.org/specializations/uva-darden-digital-product-management",
        "topics": ["product vision", "agile", "lean", "hypothesis testing", "roadmapping"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 60,
        "description": "UVA Darden product management specialization — audit for free.",
        "why_recommended": "University-quality PM curriculum, free to audit.",
    },
    # ── Agile ────────────────────────────────────────────────────────────────
    {
        "skill_name": "agile",
        "resource_name": "Agile with Atlassian Jira",
        "provider": "Atlassian / Coursera",
        "url": "https://www.coursera.org/learn/agile-atlassian-jira",
        "topics": ["scrum", "kanban", "sprint planning", "retrospectives", "Jira"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 18,
        "description": "Free Coursera course on Agile methodology using Jira from Atlassian.",
        "why_recommended": "Free to audit, practical Agile/Scrum from the makers of Jira.",
    },
    # ── UX Design ────────────────────────────────────────────────────────────
    {
        "skill_name": "ux design",
        "resource_name": "Google UX Design Professional Certificate",
        "provider": "Google / Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-ux-design",
        "topics": ["user research", "wireframing", "prototyping", "usability testing", "design thinking"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 200,
        "description": "Google's comprehensive UX design certificate — audit for free.",
        "why_recommended": "From Google, free to audit, covers the complete UX design process.",
    },
    # ── Data Structures & Algorithms ─────────────────────────────────────────
    {
        "skill_name": "data structures",
        "resource_name": "Data Structures and Algorithms Specialization",
        "provider": "Coursera / UC San Diego",
        "url": "https://www.coursera.org/specializations/data-structures-algorithms",
        "topics": ["arrays", "linked lists", "trees", "graphs", "dynamic programming", "sorting"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 120,
        "description": "UC San Diego's algorithms specialization — audit for free.",
        "why_recommended": "University-quality algorithms course, audit free.",
    },
    {
        "skill_name": "algorithms",
        "resource_name": "Algorithms, Part I & II",
        "provider": "Coursera / Princeton University",
        "url": "https://www.coursera.org/learn/algorithms-part1",
        "topics": ["sorting", "searching", "graphs", "dynamic programming", "string processing"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 80,
        "description": "Princeton's famous algorithms course by Robert Sedgewick — audit for free.",
        "why_recommended": "One of the best algorithm courses online, free to audit.",
    },
    # ── Testing ──────────────────────────────────────────────────────────────
    {
        "skill_name": "testing",
        "resource_name": "Test Automation University",
        "provider": "Applitools",
        "url": "https://testautomationu.applitools.com/",
        "topics": ["pytest", "Selenium", "Cypress", "API testing", "visual testing", "BDD"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 40,
        "description": "Free platform with 70+ courses on test automation.",
        "why_recommended": "Completely free, comprehensive, covers all major testing frameworks.",
    },
    # ── Mobile (Flutter) ─────────────────────────────────────────────────────
    {
        "skill_name": "flutter",
        "resource_name": "Flutter Documentation – Get Started",
        "provider": "Flutter Official (Google)",
        "url": "https://docs.flutter.dev/get-started/install",
        "topics": ["widgets", "state management", "navigation", "animations", "platform channels"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 10,
        "description": "Official Flutter getting-started guide from Google.",
        "why_recommended": "Free, authoritative — directly from the Flutter team.",
    },
    # ── Node.js ──────────────────────────────────────────────────────────────
    {
        "skill_name": "node.js",
        "resource_name": "Node.js Documentation",
        "provider": "Node.js Official",
        "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",
        "topics": ["event loop", "modules", "file system", "HTTP", "streams", "child processes"],
        "difficulty": "intermediate",
        "is_free": True,
        "duration_hours": 8,
        "description": "Official Node.js learning guide and API documentation.",
        "why_recommended": "Free, authoritative, straight from the Node.js foundation.",
    },
    # ── System Design ────────────────────────────────────────────────────────
    {
        "skill_name": "system design",
        "resource_name": "System Design Primer",
        "provider": "GitHub (donnemartin)",
        "url": "https://github.com/donnemartin/system-design-primer",
        "topics": ["scalability", "load balancing", "caching", "databases", "CAP theorem", "microservices"],
        "difficulty": "advanced",
        "is_free": True,
        "duration_hours": 20,
        "description": "Comprehensive open-source system design resource on GitHub.",
        "why_recommended": "Free, community-maintained, used by thousands for FAANG interviews.",
    },
    # ── Object-Oriented Programming ──────────────────────────────────────────
    {
        "skill_name": "object-oriented programming",
        "resource_name": "Object-Oriented Programming in Python",
        "provider": "Real Python",
        "url": "https://realpython.com/python3-object-oriented-programming/",
        "topics": ["classes", "inheritance", "encapsulation", "polymorphism", "dunder methods"],
        "difficulty": "beginner",
        "is_free": True,
        "duration_hours": 3,
        "description": "Free in-depth tutorial on OOP concepts in Python.",
        "why_recommended": "Free, practical, with clear examples.",
    },
    # ── Databases ────────────────────────────────────────────────────────────
    {
        "skill_name": "databases",
        "resource_name": "CMU 15-445/645 Database Systems",
        "provider": "Carnegie Mellon University",
        "url": "https://15445.courses.cs.cmu.edu/fall2023/",
        "topics": ["relational model", "query execution", "indexing", "concurrency", "recovery"],
        "difficulty": "advanced",
        "is_free": True,
        "duration_hours": 40,
        "description": "CMU's famous database systems course — full lectures and notes free online.",
        "why_recommended": "World-class university course freely available online.",
    },
    # ── Microservices ────────────────────────────────────────────────────────
    {
        "skill_name": "microservices",
        "resource_name": "Microservices with Node.js and React",
        "provider": "Udemy (Stephen Grider)",
        "url": "https://www.udemy.com/course/microservices-with-node-js-and-react/",
        "topics": ["Docker", "Kubernetes", "event-driven", "NATS", "service communication"],
        "difficulty": "advanced",
        "is_free": False,
        "duration_hours": 54,
        "description": "Comprehensive paid microservices course — regularly on sale.",
        "why_recommended": "Best-in-class practical microservices course with real projects.",
    },
]


def get_resources_for_skill(
    skill_name: str,
    max_resources: int = 3,
    preferred_difficulty: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return up to max_resources resources for the given skill name."""
    skill_lower = skill_name.lower()

    matches = [r for r in RESOURCES if r["skill_name"].lower() == skill_lower]

    if not matches:
        # Partial match fallback
        matches = [r for r in RESOURCES if skill_lower in r["skill_name"].lower()
                   or any(skill_lower in t.lower() for t in r.get("topics", []))]

    # Sort: free first, then difficulty-match
    difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    target_diff = preferred_difficulty or "beginner"
    target_idx = difficulty_order.get(target_diff, 0)

    def sort_key(r):
        free_first = 0 if r["is_free"] else 1
        diff_dist = abs(difficulty_order.get(r["difficulty"], 0) - target_idx)
        return (free_first, diff_dist)

    matches.sort(key=sort_key)
    return matches[:max_resources]


def get_resources_for_skill_gaps(
    missing_skills: List[Dict[str, Any]],
    max_per_skill: int = 2,
) -> Dict[str, List[Dict[str, Any]]]:
    """Returns a mapping of skill_name → resources for a list of gap entries."""
    result: Dict[str, List[Dict[str, Any]]] = {}
    for gap in missing_skills:
        skill = gap["skill_name"]
        importance = gap.get("importance", "important")
        # Use appropriate difficulty based on whether skill is required vs preferred
        difficulty = "beginner" if importance == "critical" else "intermediate"
        result[skill] = get_resources_for_skill(skill, max_per_skill, difficulty)
    return result


def get_all_resources() -> List[Dict[str, Any]]:
    return RESOURCES
