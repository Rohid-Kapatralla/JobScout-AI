from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env")
    exit()

print("✅ Gemini API key detected")


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

class JobSearchPlan(BaseModel):
    job_role: str = Field(
        description="The main job role or job category requested by the user."
    )

    location: str = Field(
        description="The city, region, or location where the user wants jobs."
    )

    experience_level: str = Field(
        description="Requested experience level such as Fresher, Entry Level, 0-1 years, or Experienced."
    )

    skills: list[str] = Field(
        description="Technical skills explicitly mentioned by the user."
    )

    search_keywords: list[str] = Field(
        description="Useful job-search keywords that should be used to search for relevant jobs."
    )

    search_strategy: str = Field(
        description="A short explanation of how JobScout AI should search for suitable jobs."
    )


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# JOBSCOUT AI AGENT
# ============================================================

def create_search_plan(user_request: str) -> JobSearchPlan:

    prompt = f"""
You are JobScout AI, an intelligent job research agent.

Your task is to understand a user's natural-language job-search request
and convert it into a structured job-search plan.

USER REQUEST:
{user_request}

Instructions:

1. Identify the main job role.
2. Identify the requested location.
3. Identify the experience level.
4. Extract only technical skills explicitly mentioned by the user.
5. Generate useful search keywords for finding relevant jobs.
6. Create a concise search strategy.
7. Do not invent skills that the user did not mention.
8. If the user says "fresher", interpret this as an entry-level candidate.
9. Keep the search keywords practical for a job search engine.
"""


    response = client.models.generate_content(
       model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JobSearchPlan,
        ),
    )

    return JobSearchPlan.model_validate_json(response.text)


# ============================================================
# TEST THE AGENT
# ============================================================

if __name__ == "__main__":

    user_request = """
    Find fresher Python and AI/ML jobs in Hyderabad.

    I know Python, Flask, SQL and basic machine learning.

    I want jobs suitable for someone starting their career.
    """

    try:

        plan = create_search_plan(user_request)

        print("\n" + "=" * 65)
        print("JOBSCOUT AI - SEARCH PLANNER AGENT")
        print("=" * 65)

        print("\n🔎 Job Role:")
        print(plan.job_role)

        print("\n📍 Location:")
        print(plan.location)

        print("\n🎓 Experience Level:")
        print(plan.experience_level)

        print("\n🛠️ Skills:")
        for skill in plan.skills:
            print(f"  • {skill}")

        print("\n🔍 Search Keywords:")
        for keyword in plan.search_keywords:
            print(f"  • {keyword}")

        print("\n🧠 Search Strategy:")
        print(plan.search_strategy)

        print("\n" + "=" * 65)
        print("✅ JOBSCOUT AI AGENT TEST COMPLETED")
        print("=" * 65)

    except Exception as e:

        print("\n❌ Agent request failed:")
        print(e)