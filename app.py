import os
import re
import time
from typing import Any

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import serpapi
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# =========================================================
# JOBSCOUT AI
# SerpApi India Hackathon 2026
# =========================================================

load_dotenv()

app = Flask(__name__)

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

serpapi_client = (
    serpapi.Client(api_key=SERPAPI_API_KEY)
    if SERPAPI_API_KEY
    else None
)

gemini_client = (
    genai.Client(api_key=GEMINI_API_KEY)
    if GEMINI_API_KEY
    else None
)

GEMINI_MODEL = "gemini-3.5-flash-lite"


# =========================================================
# SKILL DEFINITIONS
# =========================================================

SKILL_PATTERNS = {
    "python": [r"\bpython\b"],
    "java": [r"\bjava\b"],
    "javascript": [r"\bjavascript\b", r"\bjava\s*script\b"],
    "typescript": [r"\btypescript\b"],
    "c++": [r"\bc\+\+\b", r"\bcpp\b"],
    "c#": [r"\bc#\b", r"\bcsharp\b"],
    "html": [r"\bhtml5?\b"],
    "css": [r"\bcss3?\b"],
    "react": [r"\breact(?:\.js)?\b"],
    "node.js": [r"\bnode(?:\.js)?\b"],
    "express.js": [r"\bexpress(?:\.js)?\b"],
    "flask": [r"\bflask\b"],
    "django": [r"\bdjango\b"],
    "fastapi": [r"\bfastapi\b"],
    "spring": [r"\bspring(?:\s+boot)?\b"],
    "sql": [r"\bsql\b"],
    "mysql": [r"\bmysql\b"],
    "postgresql": [r"\bpostgres(?:ql)?\b"],
    "mongodb": [r"\bmongodb\b", r"\bmongo\s*db\b"],
    "sqlite": [r"\bsqlite\b"],
    "oracle": [r"\boracle\b"],
    "git": [r"\bgit\b"],
    "github": [r"\bgithub\b"],
    "docker": [r"\bdocker\b"],
    "aws": [r"\baws\b", r"\bamazon web services\b"],
    "azure": [r"\bazure\b"],
    "gcp": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "machine learning": [
        r"\bmachine learning\b",
        r"\bml\b",
        r"\bmachine-learning\b",
    ],
    "deep learning": [r"\bdeep learning\b"],
    "artificial intelligence": [
        r"\bartificial intelligence\b",
        r"\bai\b",
        r"\bai/ml\b",
        r"\bai-ml\b",
    ],
    "data science": [r"\bdata science\b", r"\bdata scientist\b"],
    "numpy": [r"\bnumpy\b"],
    "pandas": [r"\bpandas\b"],
    "scikit-learn": [r"\bscikit[-\s]?learn\b", r"\bsklearn\b"],
    "tensorflow": [r"\btensorflow\b"],
    "pytorch": [r"\bpytorch\b"],
    "nlp": [
        r"\bnlp\b",
        r"\bnatural language processing\b",
    ],
    "llm": [
        r"\bllm(?:s)?\b",
        r"\blarge language model(?:s)?\b",
    ],
    "generative ai": [
        r"\bgenerative ai\b",
        r"\bgenai\b",
    ],
    "rest api": [
        r"\brest(?:ful)?\s+api(?:s)?\b",
    ],
    "api": [r"\bapis?\b"],
    "bootstrap": [r"\bbootstrap\b"],
    "jinja2": [r"\bjinja2?\b"],
    "razorpay": [r"\brazorpay\b"],
}


# =========================================================
# TEXT / SKILL HELPERS
# =========================================================

def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def extract_skills(text: str) -> list[str]:
    text = normalize_text(text).lower()

    found = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for pattern in patterns
        ):
            found.append(skill)

    return sorted(set(found))


def parse_user_skills(value: Any) -> list[str]:
    if isinstance(value, list):
        raw = " ".join(str(item) for item in value)
    else:
        raw = normalize_text(value)

    detected = extract_skills(raw)

    extras = []

    for part in re.split(r"[,;\n|]+", raw):
        item = normalize_text(part).lower()

        if item and len(item) <= 40 and item not in detected:
            extras.append(item)

    return sorted(set(detected + extras))


def calculate_match(
    user_skills: list[str],
    job_skills: list[str],
) -> tuple[int, list[str], list[str]]:

    user_set = {s.lower() for s in user_skills}
    job_set = {s.lower() for s in job_skills}

    if not job_set:
        return 0, [], []

    matched = sorted(user_set.intersection(job_set))
    missing = sorted(job_set.difference(user_set))

    score = round(
        (len(matched) / len(job_set)) * 100
    )

    return score, matched, missing


def build_match_explanation(
    score: int,
    matched: list[str],
    missing: list[str],
) -> str:

    if score >= 75:
        level = "Strong skill match"
    elif score >= 50:
        level = "Good skill match"
    elif score >= 25:
        level = "Partial skill match"
    else:
        level = "Low skill match"

    if matched:
        explanation = (
            f"{level}. Matching skills: "
            f"{', '.join(matched)}."
        )
    else:
        explanation = (
            f"{level}. "
            "No matching skills were detected."
        )

    if missing:
        explanation += (
            " Common job skills not detected in "
            f"your profile: {', '.join(missing[:6])}."
        )

    return explanation


# =========================================================
# GEMINI SEARCH PLANNER
# =========================================================

class JobSearchPlan(BaseModel):
    job_role: str = Field(
        default="Software Developer"
    )

    location: str = Field(
        default="India"
    )

    experience_level: str = Field(
        default="Fresher / Entry Level"
    )

    skills: list[str] = Field(
        default_factory=list
    )

    search_keywords: list[str] = Field(
        default_factory=list
    )

    search_strategy: str = Field(
        default="Search for relevant entry-level jobs."
    )


def create_fallback_plan(
    user_request: str,
) -> JobSearchPlan:

    text = normalize_text(user_request)
    lowered = text.lower()

    location = "India"

    known_locations = [
        "Hyderabad",
        "Bengaluru",
        "Bangalore",
        "Chennai",
        "Pune",
        "Mumbai",
        "Delhi",
        "Noida",
        "Gurgaon",
        "Gurugram",
        "Kolkata",
        "Visakhapatnam",
        "Vijayawada",
        "Tirupati",
        "Remote",
    ]

    for candidate in known_locations:
        if candidate.lower() in lowered:
            location = candidate
            break

    skills = extract_skills(text)

    role = "Software Developer"

    role_candidates = [
        "Python Developer",
        "AI/ML Developer",
        "Machine Learning Engineer",
        "Data Scientist",
        "Backend Developer",
        "Web Developer",
        "Frontend Developer",
        "Full Stack Developer",
        "Software Engineer",
    ]

    for candidate in role_candidates:
        if candidate.lower() in lowered:
            role = candidate
            break

    keywords = [role]

    if (
        "fresher" in lowered
        or "entry level" in lowered
        or "graduate" in lowered
    ):
        keywords.append("Fresher / Entry Level")

    keywords.extend(skills[:5])

    return JobSearchPlan(
        job_role=role,
        location=location,
        experience_level=(
            "Fresher / Entry Level"
            if (
                "fresher" in lowered
                or "entry level" in lowered
                or "graduate" in lowered
            )
            else "Entry Level"
        ),
        skills=skills,
        search_keywords=keywords,
        search_strategy=(
            "Fallback plan generated locally "
            "from the user's request."
        ),
    )


def create_search_plan(
    user_request: str,
) -> JobSearchPlan:

    if not gemini_client:
        return create_fallback_plan(user_request)

    prompt = f"""
You are the planning component of JobScout AI.

Convert this user's natural-language job request
into a concise structured search plan.

USER REQUEST:
{user_request}

Rules:
- Extract the likely job role.
- Extract the requested city/location.
- Identify experience level such as fresher,
  entry-level, graduate, or experienced.
- Extract technical skills the user says they know.
- Create 2-6 useful search keywords.
- Do not invent a location that is not supported
  by the request.
- Use India only if no location is given.
- Keep the plan suitable for Google Jobs search.
"""

    try:

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobSearchPlan,
            ),
        )

        return JobSearchPlan.model_validate_json(
            response.text
        )

    except Exception as error:

        # Never print the raw exception.
        # SDK errors can contain sensitive URLs.
        print(
            f"Gemini planner fallback: "
            f"{type(error).__name__}"
        )

        return create_fallback_plan(user_request)


def build_search_query(
    plan: JobSearchPlan,
) -> str:

    role = (
        normalize_text(plan.job_role)
        or "Software Developer"
    )

    parts = [role]

    if plan.experience_level:

        experience = (
            plan.experience_level.lower()
        )

        if any(
            word in experience
            for word in [
                "fresher",
                "entry",
                "graduate",
                "trainee",
            ]
        ):
            parts.append("Fresher / Entry Level")

    for skill in plan.skills[:4]:

        skill = normalize_text(skill)

        if (
            skill
            and skill.lower()
            not in role.lower()
        ):
            parts.append(skill)

    query = " ".join(parts)

    return query[:180]


# =========================================================
# SERPAPI
# =========================================================

def fetch_jobs_from_serpapi(
    query: str,
    location: str,
) -> dict:
    """
    Search Google Jobs through SerpApi.

    Returns:
    {
        "jobs": [...],
        "status": "success" | "unavailable" | "error",
        "message": "..."
    }
    """

    if not serpapi_client:
        return {
            "jobs": [],
            "status": "error",
            "message": "SerpApi is not configured.",
        }

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "in",
    }

    try:
        print("SerpApi search")
        print(f"Query: {query}")
        print(f"Location: {location}")

        results = serpapi_client.search(params)

        # SerpApi's current Python SDK returns a SerpResults
        # object that behaves like a dictionary.
        jobs = results.get("jobs_results", [])

        if not isinstance(jobs, list):
            jobs = []

        print(f"SerpApi returned {len(jobs)} jobs.")

        return {
            "jobs": jobs,
            "status": "success",
            "message": f"SerpApi returned {len(jobs)} jobs.",
        }

    except Exception as error:
        print(
            "SerpApi request failed "
            f"({type(error).__name__})"
        )

        return {
            "jobs": [],
            "status": "unavailable",
            "message": (
                "Live Google Jobs search is temporarily "
                "unavailable. The AI search plan was created "
                "successfully, but SerpApi did not return "
                "live results."
            ),
        }

# =========================================================
# JOB ANALYSIS
# =========================================================

def get_job_apply_link(
    job: dict,
) -> str:

    options = job.get(
        "apply_options"
    ) or []

    if isinstance(options, list):

        for option in options:

            if (
                isinstance(option, dict)
                and option.get("link")
            ):
                return option["link"]

    return (
        job.get("share_link")
        or job.get("link")
        or ""
    )


def analyze_job(
    job: dict,
    user_skills: list[str],
) -> dict:

    title = (
        normalize_text(job.get("title"))
        or "Untitled Job"
    )

    company = (
        normalize_text(
            job.get("company_name")
        )
        or "Company not listed"
    )

    location = (
        normalize_text(
            job.get("location")
        )
        or "Location not listed"
    )

    description = normalize_text(
        job.get("description")
    )

    detected_job_skills = extract_skills(
        " ".join(
            [
                title,
                company,
                location,
                description,
                str(
                    job.get(
                        "detected_extensions"
                    )
                    or ""
                ),
            ]
        )
    )

    score, matched, missing = (
        calculate_match(
            user_skills,
            detected_job_skills,
        )
    )

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description[:1800],
        "apply_link": get_job_apply_link(job),
        "skills": detected_job_skills,
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_explanation": (
            build_match_explanation(
                score,
                matched,
                missing,
            )
        ),
        "source": (
            "Google Jobs via SerpApi"
        ),
    }


def analyze_jobs(
    jobs: list[dict],
    user_skills: list[str],
) -> list[dict]:

    analyzed = [
        analyze_job(
            job,
            user_skills,
        )
        for job in jobs[:20]
        if isinstance(job, dict)
    ]

    analyzed.sort(
        key=lambda item: (
            item.get(
                "match_score",
                0,
            ),
            item.get(
                "title",
                "",
            ),
        ),
        reverse=True,
    )

    return analyzed


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/api/health",
    methods=["GET"],
)
def health():

    return jsonify(
        {
            "status": "ok",
            "serpapi_configured": bool(
                SERPAPI_API_KEY
            ),
            "gemini_configured": bool(
                GEMINI_API_KEY
            ),
        }
    )


@app.route(
    "/test-search",
    methods=["GET"],
)
def test_search():

    result = fetch_jobs_from_serpapi(
        query="Python Developer Fresher",
        location="Hyderabad",
    )

    return jsonify(
        {
            "status": result["status"],
            "message": result["message"],
            "total_jobs": len(
                result["jobs"]
            ),
        }
    )


@app.route(
    "/api/jobs",
    methods=["POST"],
)
def api_jobs():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        # Support both old and new frontend names.
        role = normalize_text(
            data.get("job_role")
            or data.get("role")
            or "Software Developer"
        )

        location = normalize_text(
            data.get("location")
            or "India"
        )

        experience = normalize_text(
            data.get("experience")
            or data.get(
                "experience_level"
            )
            or ""
        )

        user_skills = parse_user_skills(
            data.get(
                "skills",
                "",
            )
        )

        query_parts = [role]

        if experience:
            query_parts.append(
                experience
            )

        query = " ".join(
            query_parts
        )

        result = fetch_jobs_from_serpapi(
            query,
            location,
        )

        analyzed_jobs = analyze_jobs(
            result["jobs"],
            user_skills,
        )

        return jsonify(
            {
                "status": result["status"],
                "message": result["message"],
                "query": query,
                "location": location,
                "user_skills": user_skills,
                "total_jobs": len(
                    analyzed_jobs
                ),
                "jobs": analyzed_jobs,
            }
        )

    except Exception as error:

        print(
            f"/api/jobs error: "
            f"{type(error).__name__}"
        )

        return jsonify(
            {
                "status": "error",
                "message": (
                    "Job search could not "
                    "be completed."
                ),
                "total_jobs": 0,
                "jobs": [],
            }
        ), 500


@app.route(
    "/api/agent-search",
    methods=["POST"],
)
def agent_search():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        user_query = normalize_text(
            data.get("query")
        )

        if not user_query:

            return jsonify(
                {
                    "status": "error",
                    "message": (
                        "Please provide a "
                        "natural-language "
                        "job request."
                    ),
                    "total_jobs": 0,
                    "jobs": [],
                }
            ), 400

        # 1. Gemini creates the plan.
        plan = create_search_plan(
            user_query
        )

        # 2. Collect user skills.
        user_skills = sorted(
            set(
                [
                    s.lower()
                    for s in plan.skills
                ]
                + extract_skills(
                    user_query
                )
            )
        )

        # 3. Build SerpApi query.
        query = build_search_query(
            plan
        )

        # 4. Search live jobs.
        search_result = (
            fetch_jobs_from_serpapi(
                query=query,
                location=plan.location,
            )
        )

        analyzed_jobs = analyze_jobs(
            search_result["jobs"],
            user_skills,
        )

        # SerpApi outage is returned gracefully.
        return jsonify(
            {
                "status": search_result[
                    "status"
                ],
                "message": search_result[
                    "message"
                ],
                "user_query": user_query,
                "search_plan": (
                    plan.model_dump()
                ),
                "search_query": query,
                "location": plan.location,
                "user_skills": user_skills,
                "total_jobs": len(
                    analyzed_jobs
                ),
                "jobs": analyzed_jobs,
            }
        )

    except Exception as error:

        # Never expose raw exception.
        print(
            "Agent search error: "
            f"{type(error).__name__}"
        )

        return jsonify(
            {
                "status": "error",
                "message": (
                    "The AI job search "
                    "could not be completed."
                ),
                "total_jobs": 0,
                "jobs": [],
            }
        ), 500


# =========================================================
# STARTUP
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🔎 JobScout AI")
    print("=" * 60)

    print(
        "SerpApi configured:",
        bool(SERPAPI_API_KEY),
    )

    print(
        "Gemini configured:",
        bool(GEMINI_API_KEY),
    )

    print(
        "🌐 http://127.0.0.1:5000"
    )

    print("=" * 60)

    app.run(
        debug=True
    )