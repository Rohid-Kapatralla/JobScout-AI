# 🔎 JobScout AI

> AI-powered job research assistant for students and freshers.

JobScout AI is an AI-powered job research agent that helps students and freshers discover relevant job opportunities using natural-language queries and live web search.

Instead of manually searching multiple job portals and reading hundreds of listings, users can describe what they are looking for in plain English. JobScout AI understands the request, identifies relevant skills, creates a search strategy, searches live job data, and analyzes the results against the user's skills.

---

## 🚀 Features

- 🤖 Natural-language job search
- 🧠 AI-powered search planning using Google Gemini
- 🔎 Live job discovery using SerpApi Google Jobs
- 🛠️ Automatic skill extraction
- 📊 Skill-based job matching
- ✅ Matched skills identification
- ❌ Missing skill identification
- 💡 Job-match explanations
- 🔗 Application links when available
- 🌐 Simple and responsive web interface
- ⚡ Flask-based backend

---

## 💡 Example

A user can enter:

> Find fresher Python and AI/ML jobs in Hyderabad. I know Python, Flask, SQL and basic machine learning.

JobScout AI understands the request and extracts information such as:

- Role: Python / AI/ML
- Location: Hyderabad
- Experience: Fresher
- Skills: Python, Flask, SQL, Machine Learning

It then creates a search strategy and uses live job search data to find relevant opportunities.

---

## 🏗️ How It Works

```text
User's Natural-Language Request
              ↓
       Gemini AI Planner
              ↓
        Search Strategy
              ↓
       SerpApi Google Jobs
              ↓
        Job Processing
              ↓
      Skill Extraction
              ↓
       Skill Matching
              ↓
     Match Explanation
              ↓
       Job Opportunities