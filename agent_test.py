import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

# Load environment variables from .env
load_dotenv()

# Create the JobScout AI agent
jobscout_agent = Agent(
    name="JobScout AI",
    instructions="""
    You are JobScout AI, an intelligent job research assistant.

    Your job is to help students and fresh graduates understand job-search
    requests.

    When a user gives you a job-search request:
    1. Identify the job role.
    2. Identify the location.
    3. Identify the experience level.
    4. Identify the skills mentioned by the user.
    5. Explain what you understood from the request.
    6. Suggest a concise search strategy.

    Do not invent job listings or claim that you searched the web.
    This is only a planning and intent-understanding test.
    """,
)


async def main():
    user_request = """
    Find fresher Python and AI/ML jobs in Hyderabad.
    I know Python, Flask, SQL and basic machine learning.
    I want jobs suitable for someone starting their career.
    """

    result = await Runner.run(
        jobscout_agent,
        user_request
    )

    print("\n" + "=" * 60)
    print("JOBSCOUT AI AGENT TEST")
    print("=" * 60)

    print("\nAgent response:\n")
    print(result.final_output)

    print("\n" + "=" * 60)
    print("AGENT TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())