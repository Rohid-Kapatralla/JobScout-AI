import os
from dotenv import load_dotenv
import serpapi

from jobscout_agent import create_search_plan


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not SERPAPI_API_KEY:
    print("❌ SERPAPI_API_KEY not found in .env")
    exit()

print("✅ SerpApi API key detected")


# ============================================================
# CREATE SERPAPI CLIENT
# ============================================================

client = serpapi.Client(
    api_key=SERPAPI_API_KEY
)


# ============================================================
# SERPAPI GOOGLE JOBS SEARCH
# ============================================================

def search_jobs(plan):

    role = plan.job_role
    experience = plan.experience_level

    skills = " ".join(plan.skills[:4])

    query = f"{role} {experience} {skills}"

    print("\n" + "=" * 70)
    print("🔎 SERPAPI LIVE JOB SEARCH")
    print("=" * 70)

    print(f"\nSearch query: {query}")
    print(f"Location: {plan.location}")

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": plan.location,
        "hl": "en",
        "gl": "in",
    }

    try:

        results = client.search(params)

        jobs = results.get("jobs_results", [])

        return jobs

    except serpapi.HTTPError as e:

        print("\n❌ SerpApi HTTP error:")
        print(e)

        return []

    except serpapi.TimeoutError as e:

        print("\n❌ SerpApi request timed out:")
        print(e)

        return []

    except Exception as e:

        print("\n❌ SerpApi search failed:")
        print(e)

        return []


# ============================================================
# MAIN AGENT WORKFLOW
# ============================================================

def main():

    user_request = """
    Find fresher Python and AI/ML jobs in Hyderabad.

    I know Python, Flask, SQL and basic machine learning.

    I want jobs suitable for someone starting their career.
    """

    print("\n" + "=" * 70)
    print("🤖 JOBSCOUT AI - AGENT + SERPAPI TEST")
    print("=" * 70)

    print("\nUser request:")
    print(user_request)

    # --------------------------------------------------------
    # STEP 1: GEMINI UNDERSTANDS THE REQUEST
    # --------------------------------------------------------

    print("\n🧠 Step 1: Gemini is creating a search plan...")

    try:

        plan = create_search_plan(user_request)

    except Exception as e:

        print("\n❌ Gemini agent failed:")
        print(e)

        return

    print("\n✅ Search plan created")

    print("\nJob Role:")
    print(plan.job_role)

    print("\nLocation:")
    print(plan.location)

    print("\nExperience:")
    print(plan.experience_level)

    print("\nSkills:")

    for skill in plan.skills:
        print(f"  • {skill}")

    print("\nSearch Keywords:")

    for keyword in plan.search_keywords:
        print(f"  • {keyword}")

    print("\nSearch Strategy:")
    print(plan.search_strategy)

    # --------------------------------------------------------
    # STEP 2: SERPAPI LIVE SEARCH
    # --------------------------------------------------------

    print("\n🔎 Step 2: Sending search plan to SerpApi...")

    jobs = search_jobs(plan)

    if not jobs:

        print("\n⚠️ No jobs were returned.")

        print("\nPossible reasons:")
        print("• Search returned no matching jobs")
        print("• SerpApi credits/rate limit")
        print("• Temporary API issue")
        print("• Query/location needs adjustment")

        return

    # --------------------------------------------------------
    # STEP 3: DISPLAY LIVE JOBS
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print(f"💼 LIVE JOBS FOUND: {len(jobs)}")
    print("=" * 70)

    for index, job in enumerate(jobs[:10], start=1):

        title = job.get(
            "title",
            "Unknown title"
        )

        company = job.get(
            "company_name",
            "Unknown company"
        )

        location = job.get(
            "location",
            "Location not specified"
        )

        via = job.get(
            "via",
            "Unknown source"
        )

        description = job.get(
            "description",
            ""
        )

        apply_options = job.get(
            "apply_options",
            []
        )

        apply_link = ""

        if apply_options:

            apply_link = apply_options[0].get(
                "link",
                ""
            )

        print(f"\n#{index} {title}")

        print(f"🏢 Company: {company}")

        print(f"📍 Location: {location}")

        print(f"🌐 Via: {via}")

        if apply_link:

            print(f"🔗 Apply: {apply_link}")

        if description:

            short_description = (
                description
                .replace("\n", " ")
                .strip()
            )

            if len(short_description) > 250:

                short_description = (
                    short_description[:250]
                    + "..."
                )

            print(f"📝 {short_description}")

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("✅ AGENT + SERPAPI TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print("\nJobScout AI successfully completed:")

    print("1. 🤖 Understood the user's request using Gemini")

    print("2. 🧠 Created a structured search plan")

    print("3. 🔎 Sent the plan to SerpApi")

    print("4. 🌐 Retrieved live job opportunities")

    print("5. 💼 Displayed real job listings")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()