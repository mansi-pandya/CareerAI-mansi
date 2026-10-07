"""
Question generation engine for AI interviews.

Generates 8–12 personalised questions from the student's profile.
Falls back to a rich keyword-matched question bank when no AI key is set.
"""
from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional

from app.core.config import settings


# ── Question bank ─────────────────────────────────────────────────────────────
# Each entry: {text, type, topic, difficulty, expected_answer_points}

SKILL_QUESTIONS: Dict[str, List[Dict]] = {
    "python": [
        {
            "text": "What is the difference between a list and a tuple in Python?",
            "type": "technical",
            "topic": "Python",
            "difficulty": "beginner",
            "expected_answer_points": [
                "lists are mutable; tuples are immutable",
                "tuples can be used as dictionary keys",
                "lists use square brackets; tuples use parentheses",
                "performance: tuples are slightly faster for iteration",
            ],
        },
        {
            "text": "Explain Python's GIL (Global Interpreter Lock) and its impact on multi-threaded programs.",
            "type": "technical",
            "topic": "Python Concurrency",
            "difficulty": "advanced",
            "expected_answer_points": [
                "GIL is a mutex that protects Python objects",
                "only one thread executes Python bytecode at a time",
                "CPU-bound tasks don't benefit from threads",
                "use multiprocessing or asyncio for true parallelism",
            ],
        },
        {
            "text": "What are Python decorators and how do you use them?",
            "type": "technical",
            "topic": "Python",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "decorators are functions that modify other functions",
                "use @syntax as syntactic sugar",
                "common uses: logging, authentication, caching",
                "functools.wraps preserves metadata",
            ],
        },
    ],
    "javascript": [
        {
            "text": "Explain the concept of closures in JavaScript with an example.",
            "type": "technical",
            "topic": "JavaScript",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "a closure is a function that remembers its outer scope",
                "inner function has access to outer function variables even after outer returns",
                "used for data privacy and factory functions",
                "practical example with counter or module pattern",
            ],
        },
        {
            "text": "What is the difference between 'var', 'let', and 'const' in JavaScript?",
            "type": "technical",
            "topic": "JavaScript",
            "difficulty": "beginner",
            "expected_answer_points": [
                "var is function-scoped; let and const are block-scoped",
                "var is hoisted with undefined; let/const are in temporal dead zone",
                "const cannot be reassigned (but object properties can change)",
                "prefer const by default, use let when reassignment needed",
            ],
        },
    ],
    "react": [
        {
            "text": "What is the difference between controlled and uncontrolled components in React?",
            "type": "technical",
            "topic": "React",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "controlled components: React state drives form inputs",
                "uncontrolled components: DOM manages its own state via refs",
                "controlled components give more control for validation",
                "uncontrolled simpler for simple integrations",
            ],
        },
        {
            "text": "Explain React's useEffect hook and when to use it.",
            "type": "technical",
            "topic": "React Hooks",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "used for side effects: data fetching, subscriptions, DOM manipulation",
                "dependency array controls when effect runs",
                "empty array = run once on mount",
                "cleanup function returned to prevent memory leaks",
            ],
        },
    ],
    "sql": [
        {
            "text": "Write a SQL query to find the second highest salary from an employees table.",
            "type": "coding",
            "topic": "SQL",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "use subquery with MAX() or LIMIT/OFFSET",
                "handle ties with DISTINCT",
                "alternative: window function DENSE_RANK() or RANK()",
                "consider NULL handling",
            ],
        },
        {
            "text": "What is the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN?",
            "type": "technical",
            "topic": "SQL",
            "difficulty": "beginner",
            "expected_answer_points": [
                "INNER JOIN: only matching rows from both tables",
                "LEFT JOIN: all rows from left, matching from right (NULL if no match)",
                "RIGHT JOIN: all rows from right, matching from left",
                "FULL OUTER JOIN: all rows from both tables",
            ],
        },
    ],
    "machine learning": [
        {
            "text": "Explain the bias-variance tradeoff in machine learning.",
            "type": "technical",
            "topic": "Machine Learning",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "bias: error from wrong assumptions in the model",
                "variance: error from sensitivity to training data fluctuations",
                "high bias = underfitting; high variance = overfitting",
                "goal: find sweet spot using cross-validation",
            ],
        },
        {
            "text": "What is the difference between supervised and unsupervised learning?",
            "type": "technical",
            "topic": "Machine Learning",
            "difficulty": "beginner",
            "expected_answer_points": [
                "supervised: labeled data, predict output",
                "unsupervised: unlabeled data, discover patterns",
                "examples: classification vs clustering",
                "semi-supervised combines both",
            ],
        },
    ],
    "deep learning": [
        {
            "text": "Explain how backpropagation works in a neural network.",
            "type": "technical",
            "topic": "Deep Learning",
            "difficulty": "advanced",
            "expected_answer_points": [
                "compute loss gradient with respect to each weight",
                "chain rule propagates gradients backward through layers",
                "weights updated using gradient descent",
                "learning rate controls step size",
            ],
        },
    ],
    "data structures": [
        {
            "text": "What is the time complexity of common operations on a hash table?",
            "type": "technical",
            "topic": "Data Structures",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "average case: O(1) for insert, delete, lookup",
                "worst case: O(n) due to collisions",
                "collisions handled by chaining or open addressing",
                "load factor affects performance",
            ],
        },
        {
            "text": "When would you use a stack versus a queue?",
            "type": "technical",
            "topic": "Data Structures",
            "difficulty": "beginner",
            "expected_answer_points": [
                "stack: LIFO, used for undo, recursion, DFS",
                "queue: FIFO, used for BFS, task scheduling, buffering",
                "deque supports both ends",
                "real examples from software context",
            ],
        },
    ],
    "algorithms": [
        {
            "text": "Explain the difference between BFS and DFS graph traversal.",
            "type": "technical",
            "topic": "Algorithms",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "BFS uses queue, explores level by level",
                "DFS uses stack/recursion, explores depth first",
                "BFS finds shortest path in unweighted graph",
                "DFS useful for topological sort, cycle detection",
            ],
        },
    ],
    "java": [
        {
            "text": "What is the difference between an interface and an abstract class in Java?",
            "type": "technical",
            "topic": "Java OOP",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "abstract class can have state (fields) and concrete methods",
                "interface defines a contract with default/static methods in Java 8+",
                "a class can implement multiple interfaces but extend only one class",
                "use interface for capability (flyable), abstract class for shared base",
            ],
        },
    ],
    "git": [
        {
            "text": "Explain the difference between git merge and git rebase.",
            "type": "technical",
            "topic": "Git",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "merge preserves history with a merge commit",
                "rebase rewrites commit history to linear",
                "golden rule: never rebase shared/public branches",
                "rebase makes cleaner history; merge safer for collaboration",
            ],
        },
    ],
    "docker": [
        {
            "text": "What is the difference between a Docker image and a Docker container?",
            "type": "technical",
            "topic": "Docker",
            "difficulty": "beginner",
            "expected_answer_points": [
                "image is a read-only template/blueprint",
                "container is a running instance of an image",
                "multiple containers can run from the same image",
                "containers are isolated processes on the host OS",
            ],
        },
    ],
    "rest api": [
        {
            "text": "What are the key principles of REST API design?",
            "type": "technical",
            "topic": "REST API",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "stateless: each request contains all information needed",
                "uniform interface: consistent resource naming and HTTP methods",
                "resource-based URLs (nouns not verbs)",
                "proper use of HTTP status codes",
            ],
        },
    ],
    "html": [
        {
            "text": "What is semantic HTML and why does it matter?",
            "type": "technical",
            "topic": "HTML",
            "difficulty": "beginner",
            "expected_answer_points": [
                "semantic elements describe meaning: header, nav, article, footer",
                "improves accessibility for screen readers",
                "better SEO as crawlers understand page structure",
                "makes code more readable and maintainable",
            ],
        },
    ],
    "css": [
        {
            "text": "Explain the CSS box model.",
            "type": "technical",
            "topic": "CSS",
            "difficulty": "beginner",
            "expected_answer_points": [
                "content, padding, border, margin",
                "box-sizing: border-box includes padding and border in width",
                "margin collapse between adjacent elements",
                "affects layout and spacing calculations",
            ],
        },
    ],
    "typescript": [
        {
            "text": "What are the benefits of TypeScript over JavaScript?",
            "type": "technical",
            "topic": "TypeScript",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "static type checking catches errors at compile time",
                "better IDE support and autocomplete",
                "interfaces and generics for robust code",
                "compiles to JavaScript, works everywhere",
            ],
        },
    ],
    "node.js": [
        {
            "text": "Explain the Node.js event loop.",
            "type": "technical",
            "topic": "Node.js",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "single-threaded, non-blocking I/O",
                "call stack, event queue, microtask queue",
                "libuv handles async operations",
                "setTimeout vs setImmediate vs process.nextTick",
            ],
        },
    ],
    "linux": [
        {
            "text": "What is the difference between a process and a thread in Linux?",
            "type": "technical",
            "topic": "Linux/OS",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "process has its own memory space; threads share memory",
                "threads are lighter and faster to create",
                "process communication requires IPC; threads share data directly",
                "fork() creates process; pthread_create creates thread",
            ],
        },
    ],
}

BEHAVIORAL_QUESTIONS: List[Dict] = [
    {
        "text": "Tell me about a time you faced a difficult technical challenge and how you overcame it.",
        "type": "behavioral",
        "topic": "Problem Solving",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "use STAR method: Situation, Task, Action, Result",
            "describe a specific real challenge",
            "explain your thought process and actions taken",
            "quantify the result or impact where possible",
        ],
    },
    {
        "text": "Describe a situation where you had to work in a team to complete a project. What was your role and what did you contribute?",
        "type": "behavioral",
        "topic": "Teamwork",
        "difficulty": "beginner",
        "expected_answer_points": [
            "describe the team and project context",
            "clearly state your specific role",
            "give concrete examples of contributions",
            "mention how you communicated and handled disagreements",
        ],
    },
    {
        "text": "Tell me about a time you made a mistake in a project. How did you handle it?",
        "type": "behavioral",
        "topic": "Accountability",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "be honest about the mistake without excessive self-criticism",
            "explain what led to it",
            "describe steps taken to fix it",
            "explain what you learned and how you prevent recurrence",
        ],
    },
    {
        "text": "Describe a time when you had to learn a new technology quickly for a project.",
        "type": "behavioral",
        "topic": "Learning Agility",
        "difficulty": "beginner",
        "expected_answer_points": [
            "name the technology and the context/deadline",
            "describe your learning approach",
            "explain how you applied it",
            "result of the project",
        ],
    },
    {
        "text": "Tell me about a time you had competing priorities. How did you manage them?",
        "type": "behavioral",
        "topic": "Time Management",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "describe the specific competing tasks",
            "explain your prioritization framework",
            "communicate with stakeholders",
            "outcome achieved",
        ],
    },
]

HR_QUESTIONS: List[Dict] = [
    {
        "text": "Tell me about yourself and why you are interested in this role.",
        "type": "hr",
        "topic": "Self Introduction",
        "difficulty": "beginner",
        "expected_answer_points": [
            "structured introduction: background, education, experience",
            "clear connection between skills and the role",
            "genuine motivation for the position",
            "concise (2–3 minutes)",
        ],
    },
    {
        "text": "Where do you see yourself in 5 years?",
        "type": "hr",
        "topic": "Career Goals",
        "difficulty": "beginner",
        "expected_answer_points": [
            "shows ambition and direction",
            "aligned with the company/role",
            "demonstrates commitment to growth",
            "realistic and specific",
        ],
    },
    {
        "text": "What is your greatest strength and how does it apply to this role?",
        "type": "hr",
        "topic": "Strengths",
        "difficulty": "beginner",
        "expected_answer_points": [
            "identify a genuine, relevant strength",
            "provide specific evidence or example",
            "connect clearly to the target role",
            "avoid generic answers like 'hard worker'",
        ],
    },
    {
        "text": "What is your greatest weakness, and how are you working to improve it?",
        "type": "hr",
        "topic": "Self-Awareness",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "acknowledge a genuine weakness (not a hidden strength)",
            "show self-awareness",
            "describe concrete steps taken to improve",
            "demonstrate growth mindset",
        ],
    },
    {
        "text": "Why should we hire you over other candidates?",
        "type": "hr",
        "topic": "Value Proposition",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "highlight unique combination of skills",
            "tie skills to specific job requirements",
            "show enthusiasm and cultural fit",
            "back up claims with evidence",
        ],
    },
]

CODING_BEGINNER: List[Dict] = [
    {
        "text": "Write a function to check if a string is a palindrome.",
        "type": "coding",
        "topic": "String Manipulation",
        "difficulty": "beginner",
        "expected_answer_points": [
            "compare string with its reverse",
            "handle case sensitivity",
            "handle spaces/punctuation",
            "time complexity O(n)",
        ],
    },
    {
        "text": "Given an array of integers, find the two numbers that add up to a target sum.",
        "type": "coding",
        "topic": "Arrays & Hash Maps",
        "difficulty": "beginner",
        "expected_answer_points": [
            "brute force O(n^2) nested loop approach",
            "optimal: hash map for O(n) solution",
            "explain the complement approach",
            "handle edge cases: empty array, no solution",
        ],
    },
]

CODING_INTERMEDIATE: List[Dict] = [
    {
        "text": "Implement a function to find the longest substring without repeating characters.",
        "type": "coding",
        "topic": "Sliding Window",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "sliding window technique",
            "use a set or hash map to track characters",
            "time complexity O(n)",
            "explain window expansion and contraction",
        ],
    },
    {
        "text": "Design a function to validate a balanced brackets expression (e.g., '{[()]}').",
        "type": "coding",
        "topic": "Stacks",
        "difficulty": "intermediate",
        "expected_answer_points": [
            "use a stack data structure",
            "push opening brackets, pop and match closing brackets",
            "return false if stack non-empty at end",
            "time O(n), space O(n)",
        ],
    },
]

CODING_ADVANCED: List[Dict] = [
    {
        "text": "Implement LRU (Least Recently Used) cache with O(1) get and put operations.",
        "type": "coding",
        "topic": "Design & Data Structures",
        "difficulty": "advanced",
        "expected_answer_points": [
            "use a doubly linked list + hash map",
            "hash map gives O(1) lookup",
            "linked list maintains access order",
            "move accessed node to head, evict from tail",
        ],
    },
    {
        "text": "Given a binary tree, find the lowest common ancestor of two given nodes.",
        "type": "coding",
        "topic": "Trees & Recursion",
        "difficulty": "advanced",
        "expected_answer_points": [
            "recursive DFS approach",
            "base cases: None node, node matches target",
            "if both sides return non-None, current node is LCA",
            "time O(n), space O(h)",
        ],
    },
]

CAREER_TECHNICAL_QUESTIONS: Dict[str, List[Dict]] = {
    "software engineer": [
        {
            "text": "Explain the difference between monolithic and microservices architecture.",
            "type": "technical",
            "topic": "System Design",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "monolith: single deployable unit, simpler initially",
                "microservices: independently deployable services",
                "microservices scale better but add operational complexity",
                "service communication via REST or message queues",
            ],
        },
        {
            "text": "What SOLID principles do you apply in your code and why?",
            "type": "technical",
            "topic": "Software Design",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "Single Responsibility, Open/Closed, Liskov Substitution",
                "Interface Segregation, Dependency Inversion",
                "give real example from project",
                "how they improve maintainability",
            ],
        },
    ],
    "data scientist": [
        {
            "text": "How do you handle missing data in a dataset?",
            "type": "technical",
            "topic": "Data Preprocessing",
            "difficulty": "beginner",
            "expected_answer_points": [
                "understand why data is missing (MCAR, MAR, MNAR)",
                "remove rows/columns if small percentage",
                "imputation: mean, median, mode, or model-based",
                "consider effect on downstream model",
            ],
        },
        {
            "text": "What metrics would you use to evaluate a classification model?",
            "type": "technical",
            "topic": "Model Evaluation",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "accuracy, precision, recall, F1 score",
                "ROC-AUC for ranking",
                "confusion matrix for detailed breakdown",
                "consider class imbalance when choosing metrics",
            ],
        },
    ],
    "frontend developer": [
        {
            "text": "What strategies do you use to optimize the performance of a React application?",
            "type": "technical",
            "topic": "Performance Optimization",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "React.memo and useMemo to prevent unnecessary renders",
                "code splitting with lazy() and Suspense",
                "virtualized lists for large datasets",
                "avoid anonymous functions in JSX",
            ],
        },
    ],
    "backend developer": [
        {
            "text": "How would you design a database schema for a social media platform?",
            "type": "technical",
            "topic": "Database Design",
            "difficulty": "advanced",
            "expected_answer_points": [
                "users, posts, likes, comments, followers tables",
                "indexing on frequently queried columns",
                "consider normalization vs denormalization tradeoffs",
                "scalability considerations: sharding, read replicas",
            ],
        },
    ],
    "devops engineer": [
        {
            "text": "Explain the concept of CI/CD and its benefits.",
            "type": "technical",
            "topic": "CI/CD",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "Continuous Integration: frequent code merges with automated testing",
                "Continuous Delivery/Deployment: automated release pipeline",
                "benefits: faster releases, early bug detection, reduced risk",
                "tools: Jenkins, GitHub Actions, GitLab CI",
            ],
        },
    ],
}


def _get_project_questions(projects: List[Dict]) -> List[Dict]:
    """Generate questions from student's actual project list."""
    questions = []
    for project in projects[:3]:  # max 3 project questions
        name = project.get("name", "your project")
        tech_stack = project.get("technologies", [])
        description = project.get("description", "")

        # Generic project question
        q = {
            "text": f"Walk me through your '{name}' project — what problem it solves, how you built it, and what you learned.",
            "type": "project",
            "topic": f"Project: {name}",
            "difficulty": "intermediate",
            "expected_answer_points": [
                "clearly state the problem the project solves",
                "explain technical architecture and technology choices",
                "describe challenges faced and solutions",
                "quantify impact or results",
                "mention what you'd do differently",
            ],
        }
        questions.append(q)

        # Tech-specific project question
        if tech_stack:
            main_tech = tech_stack[0] if isinstance(tech_stack, list) else str(tech_stack)
            questions.append({
                "text": f"In your '{name}' project, why did you choose {main_tech} and what were its limitations?",
                "type": "project",
                "topic": f"Project: {name} — Technology Choice",
                "difficulty": "intermediate",
                "expected_answer_points": [
                    f"justify the choice of {main_tech}",
                    "compare with alternatives considered",
                    "acknowledge real limitations or tradeoffs",
                    "show critical thinking beyond just 'I knew it'",
                ],
            })

    return questions


def _get_skill_questions(skills: List[Dict], difficulty: str, count: int = 4) -> List[Dict]:
    """Pick skill-matched questions from the question bank."""
    selected = []
    skill_names = [s.get("name", "").lower() for s in skills]

    matched_pools: List[List[Dict]] = []
    for skill_name in skill_names:
        for key, pool in SKILL_QUESTIONS.items():
            if key in skill_name or skill_name in key:
                matched_pools.append(pool)

    if not matched_pools:
        # fallback: generic technical questions
        matched_pools = list(SKILL_QUESTIONS.values())[:3]

    all_candidates = [q for pool in matched_pools for q in pool]

    # Filter by difficulty if possible
    difficulty_filtered = [q for q in all_candidates if q.get("difficulty") == difficulty]
    if len(difficulty_filtered) >= count:
        pool_to_use = difficulty_filtered
    else:
        pool_to_use = all_candidates

    selected = random.sample(pool_to_use, min(count, len(pool_to_use)))
    return selected


def _get_behavioral_questions(count: int = 2) -> List[Dict]:
    return random.sample(BEHAVIORAL_QUESTIONS, min(count, len(BEHAVIORAL_QUESTIONS)))


def _get_hr_questions(count: int = 2) -> List[Dict]:
    return random.sample(HR_QUESTIONS, min(count, len(HR_QUESTIONS)))


def _get_coding_questions(difficulty: str, count: int = 2) -> List[Dict]:
    if difficulty == "beginner":
        pool = CODING_BEGINNER
    elif difficulty == "advanced":
        pool = CODING_ADVANCED
    else:
        pool = CODING_INTERMEDIATE
    return random.sample(pool, min(count, len(pool)))


def _get_career_questions(career: str, count: int = 2) -> List[Dict]:
    career_lower = career.lower()
    for key, questions in CAREER_TECHNICAL_QUESTIONS.items():
        if key in career_lower or career_lower in key:
            return random.sample(questions, min(count, len(questions)))
    # fallback: generic software engineer questions
    fallback = CAREER_TECHNICAL_QUESTIONS.get("software engineer", [])
    return random.sample(fallback, min(count, len(fallback)))


def _compose_questions(
    interview_type: str,
    difficulty: str,
    skills: List[Dict],
    projects: List[Dict],
    career: str,
    target_count: int = 10,
) -> List[Dict]:
    """Compose question list based on interview type and student profile."""
    questions: List[Dict] = []

    if interview_type == "hr":
        questions += _get_hr_questions(4)
        questions += _get_behavioral_questions(4)
        questions += _get_career_questions(career, 2)

    elif interview_type == "behavioral":
        questions += _get_behavioral_questions(5)
        questions += _get_hr_questions(3)
        questions += _get_project_questions(projects)[:2]

    elif interview_type == "technical":
        questions += _get_skill_questions(skills, difficulty, 5)
        questions += _get_career_questions(career, 3)
        questions += _get_project_questions(projects)[:2]

    elif interview_type == "coding":
        questions += _get_coding_questions(difficulty, 4)
        questions += _get_skill_questions(skills, difficulty, 4)
        questions += _get_behavioral_questions(2)

    elif interview_type == "project_based":
        questions += _get_project_questions(projects)
        questions += _get_skill_questions(skills, difficulty, 4)
        questions += _get_behavioral_questions(2)
        questions += _get_hr_questions(2)

    else:  # mixed
        questions += _get_project_questions(projects)[:2]
        questions += _get_skill_questions(skills, difficulty, 3)
        questions += _get_career_questions(career, 2)
        questions += _get_behavioral_questions(2)
        questions += _get_hr_questions(1)
        questions += _get_coding_questions(difficulty, 1)

    # Deduplicate by text
    seen = set()
    unique = []
    for q in questions:
        key = q["text"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(q)

    # Shuffle and trim to target
    random.shuffle(unique)
    return unique[:target_count]


# ── AI generation ─────────────────────────────────────────────────────────────

async def _generate_with_ai(
    career: str,
    role: Optional[str],
    interview_type: str,
    difficulty: str,
    skills: List[Dict],
    projects: List[Dict],
    job_description: Optional[str],
) -> Optional[List[Dict]]:
    """Call AI API to generate personalised questions. Returns None on failure."""
    if not settings.AI_API_KEY:
        return None

    try:
        import httpx

        skills_str = ", ".join(s.get("name", "") for s in skills[:10])
        projects_str = "; ".join(
            f"{p.get('name','?')} ({', '.join(p.get('technologies', [])[:3])})"
            for p in projects[:4]
        )

        system = (
            "You are a professional technical interviewer. "
            "Generate interview questions personalised to the candidate's actual skills and projects. "
            "Output ONLY a JSON array of objects. Each object: "
            '{"text": "...", "type": "technical|behavioral|hr|coding|project", '
            '"topic": "...", "difficulty": "beginner|intermediate|advanced", '
            '"expected_answer_points": ["point1", "point2", ...]}'
        )

        user_msg = (
            f"Career target: {career}\n"
            f"Role: {role or 'General'}\n"
            f"Interview type: {interview_type}\n"
            f"Difficulty: {difficulty}\n"
            f"Student skills: {skills_str}\n"
            f"Student projects: {projects_str}\n"
        )
        if job_description:
            user_msg += f"Job description: {job_description[:500]}\n"
        user_msg += (
            "Generate 10 interview questions. Include project-specific questions referencing the actual project names. "
            "Make skill questions directly test the listed skills at the given difficulty level."
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
            )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Extract JSON array from content
        start = content.find("[")
        end = content.rfind("]") + 1
        if start == -1 or end == 0:
            return None
        questions = json.loads(content[start:end])
        return questions if isinstance(questions, list) else None

    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

async def generate_questions(
    career: str,
    role: Optional[str],
    interview_type: str,
    difficulty: str,
    skills: List[Dict],
    projects: List[Dict],
    job_description: Optional[str] = None,
    target_count: int = 10,
) -> List[Dict]:
    """
    Generate interview questions.

    First tries AI generation; falls back to the question bank.
    Returns a list of question dicts ready to be saved as InterviewQuestion rows.
    """
    # Try AI first
    ai_questions = await _generate_with_ai(
        career, role, interview_type, difficulty, skills, projects, job_description
    )
    if ai_questions and len(ai_questions) >= 5:
        # Normalise and cap
        result = []
        for q in ai_questions[:target_count]:
            result.append({
                "text": q.get("text", ""),
                "type": q.get("type", "technical"),
                "topic": q.get("topic", career),
                "difficulty": q.get("difficulty", difficulty),
                "expected_answer_points": q.get("expected_answer_points", []),
            })
        return result

    # Fallback: question bank
    return _compose_questions(interview_type, difficulty, skills, projects, career, target_count)
