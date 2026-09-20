from google import genai
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit()

print("✅ Gemini API key detected")

# Create Gemini client
client = genai.Client(api_key=api_key)

# Test prompt
prompt = """
You are JobScout AI, an intelligent job research assistant.

A student says:

"Find fresher Python and AI/ML jobs in Hyderabad.
I know Python, Flask, SQL and basic machine learning."

Identify:
1. Job role
2. Location
3. Experience level
4. Skills
5. A short search strategy

Keep the answer concise.
"""

try:
    response = client.models.generate_content(
       model="gemini-3.5-flash-lite",
        contents=prompt
    )

    print("\n" + "=" * 60)
    print("JOBSCOUT AI - GEMINI TEST")
    print("=" * 60)

    print("\nGemini response:\n")
    print(response.text)

    print("\n" + "=" * 60)
    print("✅ GEMINI TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)

except Exception as e:
    print("\n❌ Gemini request failed:")
    print(e)