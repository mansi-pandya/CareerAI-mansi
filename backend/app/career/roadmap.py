"""
Learning roadmap generator.

Produces phase-based roadmaps for each of the 15 career paths.
Each phase includes: skills to learn, estimated weeks, topic breakdowns, and resources.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional

from app.career.recommender import CAREER_PROFILES
from app.career.learning import get_resources_for_skill


# ── Phase templates per career ────────────────────────────────────────────────
# Each entry: {phase_number, phase_name, description, skills, estimated_weeks, topics}

CAREER_ROADMAPS: Dict[str, List[Dict[str, Any]]] = {
    "software-engineer": [
        {
            "phase_number": 1,
            "phase_name": "Foundations",
            "description": "Build core programming and computer science fundamentals.",
            "skills": ["python", "data structures", "algorithms", "git", "linux"],
            "estimated_weeks": 8,
            "topics": {
                "python": ["syntax", "functions", "OOP", "file I/O", "standard library"],
                "data structures": ["arrays", "linked lists", "stacks", "queues", "hash maps", "trees"],
                "algorithms": ["sorting", "searching", "recursion", "time complexity", "space complexity"],
                "git": ["init/clone", "branching", "merging", "pull requests", "GitHub workflow"],
                "linux": ["shell basics", "file system", "permissions", "processes", "scripting"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Core Engineering",
            "description": "Learn databases, APIs, and object-oriented design.",
            "skills": ["sql", "rest api", "object-oriented programming", "testing"],
            "estimated_weeks": 8,
            "topics": {
                "sql": ["SELECT/JOIN", "indexes", "transactions", "stored procedures", "query optimization"],
                "rest api": ["HTTP verbs", "status codes", "JSON", "authentication", "versioning"],
                "object-oriented programming": ["SOLID principles", "design patterns", "abstraction", "polymorphism"],
                "testing": ["unit tests", "integration tests", "TDD", "mocking", "pytest"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Professional Skills",
            "description": "Master system design and professional development practices.",
            "skills": ["system design", "docker", "ci/cd", "microservices"],
            "estimated_weeks": 8,
            "topics": {
                "system design": ["scalability", "load balancing", "caching", "databases at scale", "CAP theorem"],
                "docker": ["images", "containers", "Dockerfile", "docker-compose", "multi-stage builds"],
                "ci/cd": ["GitHub Actions", "automated testing", "deployment pipelines", "environment management"],
                "microservices": ["service decomposition", "API gateway", "event-driven", "service mesh"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Specialization & Cloud",
            "description": "Deepen expertise in cloud and advanced engineering.",
            "skills": ["aws", "kubernetes", "agile"],
            "estimated_weeks": 6,
            "topics": {
                "aws": ["EC2", "S3", "Lambda", "RDS", "CloudFormation", "IAM"],
                "kubernetes": ["pods", "deployments", "services", "ingress", "helm", "monitoring"],
                "agile": ["scrum", "sprint planning", "retrospectives", "estimation", "user stories"],
            },
        },
    ],

    "frontend-developer": [
        {
            "phase_number": 1,
            "phase_name": "HTML & CSS Mastery",
            "description": "Build solid HTML/CSS foundations with responsive design.",
            "skills": ["html", "css", "responsive design"],
            "estimated_weeks": 6,
            "topics": {
                "html": ["semantic HTML5", "forms", "accessibility", "SEO basics", "meta tags"],
                "css": ["box model", "Flexbox", "CSS Grid", "custom properties", "animations"],
                "responsive design": ["media queries", "mobile-first", "viewport", "fluid layouts", "breakpoints"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "JavaScript & Modern Tooling",
            "description": "Master JavaScript and set up a modern development environment.",
            "skills": ["javascript", "typescript", "git"],
            "estimated_weeks": 8,
            "topics": {
                "javascript": ["ES6+", "async/await", "promises", "DOM manipulation", "modules", "closures"],
                "typescript": ["types", "interfaces", "generics", "strict mode", "utility types"],
                "git": ["branching strategies", "code review", "GitHub workflow", "conventional commits"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "React Ecosystem",
            "description": "Build modern, production-ready React applications.",
            "skills": ["react", "rest api", "testing"],
            "estimated_weeks": 10,
            "topics": {
                "react": ["components", "hooks", "context", "react-router", "state management", "performance"],
                "rest api": ["fetch/axios", "authentication", "error handling", "loading states", "caching"],
                "testing": ["React Testing Library", "Jest", "component testing", "integration testing"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Production Readiness",
            "description": "Optimize, deploy, and refine your frontend skills.",
            "skills": ["performance optimization", "accessibility", "figma", "ci/cd"],
            "estimated_weeks": 6,
            "topics": {
                "performance optimization": ["code splitting", "lazy loading", "caching", "Core Web Vitals", "Lighthouse"],
                "accessibility": ["ARIA", "keyboard navigation", "screen readers", "WCAG 2.1", "color contrast"],
                "figma": ["inspect mode", "design tokens", "prototypes", "developer handoff"],
                "ci/cd": ["GitHub Actions", "deployment to Vercel/Netlify", "environment variables"],
            },
        },
    ],

    "backend-developer": [
        {
            "phase_number": 1,
            "phase_name": "Programming & Data",
            "description": "Master Python, databases, and core backend concepts.",
            "skills": ["python", "sql", "databases", "linux"],
            "estimated_weeks": 8,
            "topics": {
                "python": ["OOP", "async", "decorators", "type hints", "standard library"],
                "sql": ["complex joins", "indexes", "transactions", "window functions", "optimization"],
                "databases": ["PostgreSQL", "MySQL", "normalization", "ACID", "connection pooling"],
                "linux": ["process management", "networking", "cron", "systemd", "monitoring"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "APIs & Backend Frameworks",
            "description": "Build production APIs with authentication and security.",
            "skills": ["rest api", "authentication", "git", "testing"],
            "estimated_weeks": 8,
            "topics": {
                "rest api": ["FastAPI/Django/Flask", "OpenAPI", "versioning", "rate limiting", "pagination"],
                "authentication": ["JWT", "OAuth2", "session management", "password hashing", "2FA"],
                "git": ["feature branches", "code review", "CI integration"],
                "testing": ["pytest", "test fixtures", "mocking", "API testing", "coverage"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Infrastructure & Scale",
            "description": "Deploy and scale backend services.",
            "skills": ["docker", "redis", "microservices", "ci/cd"],
            "estimated_weeks": 8,
            "topics": {
                "docker": ["multi-stage builds", "Docker Compose", "environment configuration", "health checks"],
                "redis": ["caching strategies", "pub/sub", "session storage", "rate limiting", "TTL"],
                "microservices": ["service boundaries", "async messaging", "saga pattern", "health checks"],
                "ci/cd": ["automated testing", "staged deployments", "rollback strategies", "blue-green"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Cloud & Advanced Patterns",
            "description": "Deploy to cloud and apply advanced backend patterns.",
            "skills": ["aws", "kubernetes", "security"],
            "estimated_weeks": 6,
            "topics": {
                "aws": ["RDS", "ElastiCache", "ECS/EKS", "SQS/SNS", "Lambda", "API Gateway"],
                "kubernetes": ["stateful applications", "secrets management", "autoscaling", "monitoring"],
                "security": ["OWASP Top 10", "SQL injection", "XSS", "CORS", "dependency scanning"],
            },
        },
    ],

    "full-stack-developer": [
        {
            "phase_number": 1,
            "phase_name": "Web Fundamentals",
            "description": "Master HTML, CSS, JavaScript and version control.",
            "skills": ["html", "css", "javascript", "git"],
            "estimated_weeks": 8,
            "topics": {
                "html": ["semantic HTML5", "forms", "accessibility"],
                "css": ["Flexbox", "Grid", "responsive design", "animations"],
                "javascript": ["ES6+", "DOM", "async/await", "modules"],
                "git": ["branching", "merging", "GitHub workflow"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Frontend Framework",
            "description": "Build interactive UIs with React.",
            "skills": ["react", "typescript", "rest api"],
            "estimated_weeks": 8,
            "topics": {
                "react": ["hooks", "context", "routing", "state management", "forms"],
                "typescript": ["types", "interfaces", "generics", "React TypeScript patterns"],
                "rest api": ["HTTP", "fetch", "authentication flows", "error handling"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Backend & Databases",
            "description": "Build server-side logic and data persistence.",
            "skills": ["python", "sql", "databases", "authentication"],
            "estimated_weeks": 8,
            "topics": {
                "python": ["FastAPI/Django", "ORM", "async", "type hints"],
                "sql": ["JOIN", "indexes", "transactions", "migrations"],
                "databases": ["PostgreSQL", "Redis", "connection pooling"],
                "authentication": ["JWT", "OAuth2", "session vs token", "RBAC"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "DevOps & Deployment",
            "description": "Deploy full-stack applications with CI/CD.",
            "skills": ["docker", "ci/cd", "testing"],
            "estimated_weeks": 6,
            "topics": {
                "docker": ["Dockerfile", "Compose", "multi-stage", "registries"],
                "ci/cd": ["GitHub Actions", "automated testing", "staging environments"],
                "testing": ["unit", "integration", "e2e with Playwright/Cypress"],
            },
        },
    ],

    "data-analyst": [
        {
            "phase_number": 1,
            "phase_name": "Data Foundations",
            "description": "Learn Python, SQL, and data manipulation fundamentals.",
            "skills": ["python", "sql", "excel", "pandas"],
            "estimated_weeks": 8,
            "topics": {
                "python": ["Jupyter", "variables", "loops", "functions", "file handling"],
                "sql": ["SELECT", "JOINs", "GROUP BY", "subqueries", "window functions"],
                "excel": ["pivot tables", "VLOOKUP", "charts", "formulas", "data cleaning"],
                "pandas": ["DataFrames", "filtering", "groupby", "merging", "datetime"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Analysis & Visualization",
            "description": "Derive insights and build compelling visualizations.",
            "skills": ["data visualization", "statistics", "numpy"],
            "estimated_weeks": 8,
            "topics": {
                "data visualization": ["matplotlib", "seaborn", "Plotly", "chart selection", "dashboards"],
                "statistics": ["mean/median/mode", "standard deviation", "distributions", "hypothesis testing"],
                "numpy": ["arrays", "broadcasting", "linear algebra", "random sampling"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "BI Tools & Reporting",
            "description": "Build professional dashboards and automated reports.",
            "skills": ["tableau", "power bi", "data cleaning"],
            "estimated_weeks": 6,
            "topics": {
                "tableau": ["calculated fields", "LOD expressions", "dashboards", "story points", "publishing"],
                "power bi": ["Power Query", "DAX", "relationships", "report design", "sharing"],
                "data cleaning": ["missing values", "outliers", "duplicates", "normalization", "validation"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Advanced Analysis",
            "description": "A/B testing, business intelligence, and ML basics.",
            "skills": ["a/b testing", "business intelligence", "machine learning"],
            "estimated_weeks": 6,
            "topics": {
                "a/b testing": ["experimental design", "sample size", "p-values", "significance", "Bayesian"],
                "business intelligence": ["KPIs", "metrics frameworks", "OLAP", "data warehouse", "star schema"],
                "machine learning": ["linear regression", "feature engineering", "model evaluation", "scikit-learn"],
            },
        },
    ],

    "data-scientist": [
        {
            "phase_number": 1,
            "phase_name": "Math & Programming Foundations",
            "description": "Build strong mathematical and Python programming foundations.",
            "skills": ["python", "statistics", "numpy", "pandas"],
            "estimated_weeks": 10,
            "topics": {
                "python": ["OOP", "generators", "decorators", "type hints"],
                "statistics": ["probability", "distributions", "Bayesian inference", "hypothesis testing"],
                "numpy": ["linear algebra", "matrix operations", "random", "vectorization"],
                "pandas": ["advanced indexing", "reshaping", "time series", "performance"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Machine Learning Core",
            "description": "Master classical ML algorithms and feature engineering.",
            "skills": ["machine learning", "scikit-learn", "feature engineering", "data visualization"],
            "estimated_weeks": 10,
            "topics": {
                "machine learning": ["supervised learning", "unsupervised learning", "model selection", "cross-validation"],
                "scikit-learn": ["pipelines", "preprocessing", "grid search", "model evaluation"],
                "feature engineering": ["encoding", "scaling", "feature selection", "imputation"],
                "data visualization": ["exploratory analysis", "Plotly", "storytelling with data"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Deep Learning & NLP",
            "description": "Apply deep learning and natural language processing.",
            "skills": ["deep learning", "tensorflow", "nlp", "pytorch"],
            "estimated_weeks": 10,
            "topics": {
                "deep learning": ["neural networks", "CNN", "RNN", "LSTM", "backpropagation"],
                "tensorflow": ["Keras", "training loops", "model saving", "TensorBoard"],
                "nlp": ["tokenization", "embeddings", "transformers", "sentiment", "named entity"],
                "pytorch": ["autograd", "custom datasets", "transfer learning"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Production & Experimentation",
            "description": "Deploy models and run real experiments.",
            "skills": ["sql", "a/b testing", "experiment design", "cloud"],
            "estimated_weeks": 8,
            "topics": {
                "sql": ["complex analytics queries", "window functions", "CTEs"],
                "a/b testing": ["power analysis", "online experiments", "causal inference"],
                "experiment design": ["DOE", "confounders", "metrics", "counterfactuals"],
                "cloud": ["Vertex AI", "SageMaker", "Azure ML", "model endpoints"],
            },
        },
    ],

    "machine-learning-engineer": [
        {
            "phase_number": 1,
            "phase_name": "ML & Software Foundations",
            "description": "Build strong ML and software engineering fundamentals.",
            "skills": ["python", "machine learning", "scikit-learn", "sql"],
            "estimated_weeks": 8,
            "topics": {
                "python": ["type hints", "async", "packaging", "profiling"],
                "machine learning": ["core algorithms", "bias-variance", "ensemble methods", "AutoML"],
                "scikit-learn": ["custom transformers", "pipelines", "model persistence"],
                "sql": ["large dataset queries", "aggregations", "window functions"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Deep Learning & Frameworks",
            "description": "Master PyTorch and TensorFlow for production DL.",
            "skills": ["pytorch", "tensorflow", "deep learning", "feature engineering"],
            "estimated_weeks": 10,
            "topics": {
                "pytorch": ["custom layers", "distributed training", "ONNX export", "inference optimization"],
                "tensorflow": ["SavedModel", "TFX", "TFLite", "serving"],
                "deep learning": ["architectures", "transfer learning", "attention mechanisms"],
                "feature engineering": ["embeddings", "feature stores", "online vs batch features"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "MLOps & Deployment",
            "description": "Deploy and monitor ML models at scale.",
            "skills": ["mlops", "model deployment", "docker", "model monitoring"],
            "estimated_weeks": 8,
            "topics": {
                "mlops": ["experiment tracking (MLflow)", "model registry", "data versioning (DVC)", "pipelines"],
                "model deployment": ["REST APIs", "FastAPI", "batch inference", "streaming inference"],
                "docker": ["ML containers", "GPU support", "multi-stage builds"],
                "model monitoring": ["data drift", "concept drift", "model degradation", "alerting"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Scale & Cloud",
            "description": "Run ML workloads at scale on cloud platforms.",
            "skills": ["kubernetes", "distributed computing", "cloud"],
            "estimated_weeks": 8,
            "topics": {
                "kubernetes": ["Kubeflow", "GPU nodes", "model serving", "autoscaling"],
                "distributed computing": ["Spark ML", "Ray", "Dask", "data parallelism"],
                "cloud": ["SageMaker", "Vertex AI", "Azure ML", "managed endpoints"],
            },
        },
    ],

    "ai-engineer": [
        {
            "phase_number": 1,
            "phase_name": "AI & LLM Foundations",
            "description": "Understand LLMs, prompt engineering, and AI APIs.",
            "skills": ["python", "llm", "prompt engineering", "openai api"],
            "estimated_weeks": 6,
            "topics": {
                "python": ["async", "type hints", "API clients"],
                "llm": ["transformer architecture", "tokenization", "context windows", "temperature"],
                "prompt engineering": ["system prompts", "few-shot", "chain-of-thought", "output formatting"],
                "openai api": ["chat completions", "embeddings", "function calling", "rate limits"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "RAG & AI Applications",
            "description": "Build retrieval-augmented generation and AI-powered apps.",
            "skills": ["langchain", "vector databases", "rag", "rest api"],
            "estimated_weeks": 8,
            "topics": {
                "langchain": ["chains", "agents", "memory", "tools", "callbacks"],
                "vector databases": ["embeddings", "similarity search", "Pinecone/Chroma/Weaviate", "indexing"],
                "rag": ["chunking strategies", "retrieval", "re-ranking", "evaluation"],
                "rest api": ["FastAPI", "async endpoints", "streaming responses", "auth"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Fine-Tuning & Hugging Face",
            "description": "Customize models for specific use cases.",
            "skills": ["fine-tuning", "hugging face", "deep learning", "docker"],
            "estimated_weeks": 8,
            "topics": {
                "fine-tuning": ["PEFT", "LoRA", "QLoRA", "dataset preparation", "evaluation"],
                "hugging face": ["transformers", "datasets", "model hub", "Inference API"],
                "deep learning": ["attention", "encoder-decoder", "BERT", "GPT architecture"],
                "docker": ["GPU containers", "model serving", "environment management"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Production AI Systems",
            "description": "Deploy and scale AI systems in production.",
            "skills": ["kubernetes", "cloud", "model monitoring"],
            "estimated_weeks": 6,
            "topics": {
                "kubernetes": ["AI inference servers", "GPU scheduling", "autoscaling", "cost management"],
                "cloud": ["AWS Bedrock", "Azure OpenAI", "Vertex AI", "managed AI services"],
                "model monitoring": ["hallucination detection", "output quality", "cost monitoring", "latency"],
            },
        },
    ],

    "cloud-engineer": [
        {
            "phase_number": 1,
            "phase_name": "Cloud Fundamentals",
            "description": "Understand core cloud concepts and foundational services.",
            "skills": ["aws", "linux", "networking"],
            "estimated_weeks": 8,
            "topics": {
                "aws": ["global infrastructure", "EC2", "S3", "VPC", "IAM", "pricing"],
                "linux": ["shell scripting", "networking", "systemd", "monitoring tools"],
                "networking": ["TCP/IP", "DNS", "CIDR", "VPN", "load balancers", "CDN"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Infrastructure as Code",
            "description": "Automate infrastructure provisioning with Terraform.",
            "skills": ["terraform", "iam", "cloud architecture"],
            "estimated_weeks": 8,
            "topics": {
                "terraform": ["providers", "resources", "state management", "modules", "workspaces"],
                "iam": ["users/groups/roles", "policies", "least privilege", "federation", "service accounts"],
                "cloud architecture": ["well-architected framework", "availability zones", "disaster recovery"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Containers & Orchestration",
            "description": "Deploy containerized workloads at scale.",
            "skills": ["docker", "kubernetes", "ci/cd"],
            "estimated_weeks": 8,
            "topics": {
                "docker": ["multi-stage builds", "registries", "security scanning"],
                "kubernetes": ["EKS/AKS/GKE", "deployments", "autoscaling", "ingress", "service mesh"],
                "ci/cd": ["GitHub Actions", "ArgoCD", "GitOps", "blue-green deployments"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Multi-Cloud & Advanced",
            "description": "Manage multi-cloud deployments and cost optimization.",
            "skills": ["azure", "gcp", "multi-cloud", "cost optimization"],
            "estimated_weeks": 6,
            "topics": {
                "azure": ["AKS", "Azure DevOps", "Azure Networking", "ARM templates"],
                "gcp": ["GKE", "Cloud Run", "BigQuery", "Cloud Storage"],
                "multi-cloud": ["cloud-agnostic tooling", "vendor lock-in", "data sovereignty"],
                "cost optimization": ["reserved instances", "spot instances", "rightsizing", "tagging"],
            },
        },
    ],

    "devops-engineer": [
        {
            "phase_number": 1,
            "phase_name": "Linux & Scripting",
            "description": "Master Linux administration and shell scripting.",
            "skills": ["linux", "bash", "git"],
            "estimated_weeks": 6,
            "topics": {
                "linux": ["file system", "process management", "networking", "security", "performance"],
                "bash": ["scripting", "functions", "conditionals", "loops", "cron jobs"],
                "git": ["branching strategies", "hooks", "submodules", "monorepo"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Containers & Orchestration",
            "description": "Deploy and manage containerized applications.",
            "skills": ["docker", "kubernetes", "ci/cd"],
            "estimated_weeks": 8,
            "topics": {
                "docker": ["images", "networking", "volumes", "security", "multi-stage"],
                "kubernetes": ["cluster setup", "deployments", "services", "ingress", "RBAC"],
                "ci/cd": ["Jenkins", "GitHub Actions", "GitLab CI", "pipelines as code"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Infrastructure & Cloud",
            "description": "Automate infrastructure and manage cloud environments.",
            "skills": ["terraform", "aws", "ansible"],
            "estimated_weeks": 8,
            "topics": {
                "terraform": ["modules", "state locking", "remote state", "policy as code"],
                "aws": ["EC2", "ECS", "RDS", "ElastiCache", "CloudWatch"],
                "ansible": ["playbooks", "roles", "inventories", "vault", "AWX"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Monitoring & SRE",
            "description": "Implement observability and site reliability practices.",
            "skills": ["monitoring", "prometheus", "grafana", "security"],
            "estimated_weeks": 6,
            "topics": {
                "monitoring": ["metrics", "logs", "traces", "SLOs/SLAs/SLIs", "on-call"],
                "prometheus": ["scraping", "PromQL", "alerting rules", "exporters"],
                "grafana": ["dashboards", "panels", "data sources", "alerting"],
                "security": ["DevSecOps", "SAST/DAST", "container scanning", "secrets management"],
            },
        },
    ],

    "qa-engineer": [
        {
            "phase_number": 1,
            "phase_name": "Testing Fundamentals",
            "description": "Understand testing principles and manual testing techniques.",
            "skills": ["testing", "bug tracking", "sql"],
            "estimated_weeks": 6,
            "topics": {
                "testing": ["test types", "test design techniques", "boundary value analysis", "equivalence partitioning"],
                "bug tracking": ["Jira", "defect lifecycle", "severity/priority", "root cause analysis"],
                "sql": ["data verification", "test data generation", "query analysis"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Test Automation",
            "description": "Automate UI and API tests.",
            "skills": ["selenium", "python", "api testing"],
            "estimated_weeks": 8,
            "topics": {
                "selenium": ["WebDriver", "page objects", "waits", "cross-browser", "grid"],
                "python": ["pytest", "fixtures", "parameterization", "reporting"],
                "api testing": ["Postman", "REST-assured", "contract testing", "authentication"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Modern Testing Tools",
            "description": "Use modern testing frameworks and CI integration.",
            "skills": ["cypress", "playwright", "ci/cd"],
            "estimated_weeks": 6,
            "topics": {
                "cypress": ["component testing", "network stubbing", "visual testing", "reporters"],
                "playwright": ["multi-browser", "mobile emulation", "tracing", "screenshots"],
                "ci/cd": ["test reporting", "parallel runs", "flaky test detection", "test in pipeline"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Advanced QA",
            "description": "Performance, security, and mobile testing.",
            "skills": ["performance testing", "security testing", "mobile testing"],
            "estimated_weeks": 6,
            "topics": {
                "performance testing": ["JMeter", "k6", "load testing", "stress testing", "profiling"],
                "security testing": ["OWASP ZAP", "SQL injection", "XSS", "SAST integration"],
                "mobile testing": ["Appium", "device farms", "platform-specific issues"],
            },
        },
    ],

    "mobile-developer": [
        {
            "phase_number": 1,
            "phase_name": "Mobile Fundamentals",
            "description": "Choose your platform and learn the fundamentals.",
            "skills": ["flutter", "dart", "git"],
            "estimated_weeks": 8,
            "topics": {
                "flutter": ["widgets", "Material Design", "navigation", "state basics"],
                "dart": ["syntax", "OOP", "async/await", "streams"],
                "git": ["mobile workflow", "feature branches", "code review"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "State Management & APIs",
            "description": "Manage complex state and integrate backend APIs.",
            "skills": ["rest api", "mobile ui", "animations"],
            "estimated_weeks": 8,
            "topics": {
                "rest api": ["Dio/http", "authentication", "caching", "offline support"],
                "mobile ui": ["custom widgets", "theming", "responsive layouts", "accessibility"],
                "animations": ["implicit animations", "Hero", "staggered", "custom painters"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Native Features & Firebase",
            "description": "Integrate device features and cloud services.",
            "skills": ["firebase", "push notifications", "in-app purchases"],
            "estimated_weeks": 6,
            "topics": {
                "firebase": ["Auth", "Firestore", "Crashlytics", "Remote Config", "Analytics"],
                "push notifications": ["FCM", "local notifications", "background handling"],
                "in-app purchases": ["RevenueCat", "subscription management", "receipt validation"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Deployment & Quality",
            "description": "Test, optimize, and publish your mobile app.",
            "skills": ["testing", "performance", "app store deployment", "ci/cd"],
            "estimated_weeks": 6,
            "topics": {
                "testing": ["widget tests", "integration tests", "golden tests"],
                "performance": ["memory leaks", "render jank", "startup time", "profiling"],
                "app store deployment": ["signing", "build variants", "app review guidelines"],
                "ci/cd": ["Fastlane", "GitHub Actions", "automated testing in pipeline"],
            },
        },
    ],

    "cybersecurity-analyst": [
        {
            "phase_number": 1,
            "phase_name": "Security Foundations",
            "description": "Build core security and networking foundations.",
            "skills": ["networking", "linux", "vulnerability assessment"],
            "estimated_weeks": 8,
            "topics": {
                "networking": ["TCP/IP", "protocols", "Wireshark", "packet analysis"],
                "linux": ["hardening", "logs", "file permissions", "network tools"],
                "vulnerability assessment": ["Nmap", "Nessus", "CVSS scoring", "patch management"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Threat Detection & Response",
            "description": "Monitor, detect, and respond to security incidents.",
            "skills": ["security monitoring", "siem", "incident response"],
            "estimated_weeks": 8,
            "topics": {
                "security monitoring": ["log analysis", "baselines", "anomaly detection", "alerts"],
                "siem": ["Splunk", "ELK", "correlation rules", "dashboards", "log ingestion"],
                "incident response": ["IR lifecycle", "forensic preservation", "containment", "eradication"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Offensive Security",
            "description": "Learn penetration testing and ethical hacking.",
            "skills": ["penetration testing", "firewalls", "cryptography"],
            "estimated_weeks": 8,
            "topics": {
                "penetration testing": ["recon", "exploitation (Metasploit)", "post-exploitation", "reporting"],
                "firewalls": ["rule management", "IDS/IPS", "WAF", "next-gen firewalls"],
                "cryptography": ["symmetric/asymmetric", "TLS", "PKI", "hashing", "key management"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Advanced & Cloud Security",
            "description": "Apply threat intelligence and secure cloud environments.",
            "skills": ["cloud security", "threat intelligence", "forensics"],
            "estimated_weeks": 6,
            "topics": {
                "cloud security": ["IAM", "AWS GuardDuty", "Azure Defender", "CSPM", "zero trust"],
                "threat intelligence": ["MITRE ATT&CK", "threat actors", "IOCs", "CTI feeds"],
                "forensics": ["disk forensics", "memory forensics", "timeline analysis", "chain of custody"],
            },
        },
    ],

    "product-manager": [
        {
            "phase_number": 1,
            "phase_name": "PM Fundamentals",
            "description": "Understand the product manager role and frameworks.",
            "skills": ["product strategy", "agile", "communication"],
            "estimated_weeks": 6,
            "topics": {
                "product strategy": ["product vision", "north star", "OKRs", "competitive analysis", "positioning"],
                "agile": ["scrum", "kanban", "sprint ceremonies", "backlog refinement", "estimation"],
                "communication": ["stakeholder updates", "PRDs", "executive summaries", "Confluence"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "User Research & Discovery",
            "description": "Validate product ideas through user research.",
            "skills": ["user research", "roadmapping", "stakeholder management"],
            "estimated_weeks": 6,
            "topics": {
                "user research": ["user interviews", "surveys", "usability testing", "personas", "jobs-to-be-done"],
                "roadmapping": ["prioritization frameworks (RICE/ICE)", "quarterly roadmaps", "now/next/later"],
                "stakeholder management": ["alignment", "influence without authority", "conflict resolution"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "Data-Driven Product",
            "description": "Use data to measure product success and drive decisions.",
            "skills": ["data analysis", "a/b testing", "sql"],
            "estimated_weeks": 6,
            "topics": {
                "data analysis": ["funnel analysis", "cohort analysis", "retention", "KPI dashboards"],
                "a/b testing": ["hypothesis formation", "statistical significance", "MVTs", "analyzing results"],
                "sql": ["product metrics queries", "user behavior analysis", "funnels in SQL"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Go-to-Market & Growth",
            "description": "Launch products and drive growth.",
            "skills": ["market research", "pricing", "business analysis", "figma"],
            "estimated_weeks": 6,
            "topics": {
                "market research": ["TAM/SAM/SOM", "competitive intelligence", "market sizing"],
                "pricing": ["pricing models", "willingness to pay", "packaging strategy"],
                "business analysis": ["ROI", "business cases", "P&L basics", "unit economics"],
                "figma": ["low-fi wireframes", "developer handoff", "design feedback"],
            },
        },
    ],

    "ui-ux-designer": [
        {
            "phase_number": 1,
            "phase_name": "Design Foundations",
            "description": "Build core visual design and UX fundamentals.",
            "skills": ["ui design", "ux design", "design systems"],
            "estimated_weeks": 8,
            "topics": {
                "ui design": ["typography", "color theory", "spacing", "layout", "visual hierarchy"],
                "ux design": ["design thinking", "user journey mapping", "information architecture", "mental models"],
                "design systems": ["components", "tokens", "Storybook", "documentation", "governance"],
            },
        },
        {
            "phase_number": 2,
            "phase_name": "Figma & Prototyping",
            "description": "Master Figma and create interactive prototypes.",
            "skills": ["figma", "wireframing", "prototyping"],
            "estimated_weeks": 6,
            "topics": {
                "figma": ["auto layout", "components", "variants", "plugins", "collaborative design"],
                "wireframing": ["low-fi wireframes", "sketching", "mid-fi screens", "annotation"],
                "prototyping": ["interactive flows", "micro-interactions", "smart animate", "usability scripts"],
            },
        },
        {
            "phase_number": 3,
            "phase_name": "User Research",
            "description": "Conduct research and make data-driven design decisions.",
            "skills": ["user research", "usability testing", "accessibility"],
            "estimated_weeks": 6,
            "topics": {
                "user research": ["qualitative methods", "quantitative methods", "affinity mapping", "synthesis"],
                "usability testing": ["moderated testing", "unmoderated testing", "task analysis", "reporting"],
                "accessibility": ["WCAG 2.1 AA", "color contrast", "keyboard navigation", "ARIA", "screen readers"],
            },
        },
        {
            "phase_number": 4,
            "phase_name": "Shipping & Measuring",
            "description": "Collaborate with engineers and measure design impact.",
            "skills": ["html", "css", "motion design"],
            "estimated_weeks": 6,
            "topics": {
                "html": ["semantic markup", "developer handoff", "design-to-code inspection"],
                "css": ["basics for collaboration", "variables", "animation basics"],
                "motion design": ["transition principles", "easing", "Lottie", "micro-interactions"],
            },
        },
    ],
}


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_roadmap(
    career_slug: str,
    student_skills: List[Dict[str, Any]],
    user_id: int,
    career_id: int,
) -> Dict[str, Any]:
    """
    Generate a personalized learning roadmap.

    Phases that the student has already completed (all skills matched) are
    flagged. Resource links are attached per skill from the learning database.
    """
    profile = CAREER_PROFILES.get(career_slug)
    if not profile:
        return {"error": f"Unknown career slug: {career_slug}"}

    template_phases = CAREER_ROADMAPS.get(career_slug, [])
    student_skill_names = {s["name"].lower() for s in student_skills}

    enriched_phases = []
    for phase in template_phases:
        skills_done = [s for s in phase["skills"] if s.lower() in student_skill_names]
        skills_todo = [s for s in phase["skills"] if s.lower() not in student_skill_names]
        completed = len(skills_done) == len(phase["skills"])

        # Attach resources per skill
        skill_resources: Dict[str, List[Dict[str, Any]]] = {}
        for skill in phase["skills"]:
            resources = get_resources_for_skill(skill, max_resources=2)
            if resources:
                skill_resources[skill] = [
                    {
                        "resource_name": r["resource_name"],
                        "provider": r["provider"],
                        "url": r["url"],
                        "is_free": r["is_free"],
                        "difficulty": r["difficulty"],
                        "duration_hours": r["duration_hours"],
                    }
                    for r in resources
                ]

        enriched_phases.append({
            "phase_number": phase["phase_number"],
            "phase_name": phase["phase_name"],
            "description": phase["description"],
            "skills": phase["skills"],
            "skills_done": skills_done,
            "skills_todo": skills_todo,
            "estimated_weeks": phase["estimated_weeks"],
            "topics": phase.get("topics", {}),
            "resources": skill_resources,
            "completed": completed,
            "progress_pct": round(len(skills_done) / max(len(phase["skills"]), 1) * 100),
        })

    total_weeks = sum(p["estimated_weeks"] for p in template_phases)
    total_skills = sum(len(p["skills"]) for p in template_phases)
    completed_skills = sum(len(p["skills_done"]) for p in enriched_phases)
    overall_progress = round(completed_skills / max(total_skills, 1) * 100)

    return {
        "user_id": user_id,
        "career_id": career_id,
        "career_slug": career_slug,
        "career_name": profile["name"],
        "title": f"Learning Roadmap: {profile['name']}",
        "phases": enriched_phases,
        "total_weeks": total_weeks,
        "total_skills": total_skills,
        "completed_skills": completed_skills,
        "overall_progress": overall_progress,
    }
