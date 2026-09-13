from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

job_analyzer = Agent(
    name = "job_analyzer",
    model = Gemini(
        model = MODEL,
        retry_options = types.HttpRetryOptions(attempts = 3),
    ),
    instruction = """
    You are the Job Analyzer for JobPilot AI.

    Analyze the provided job description.

    Extract:
    - Job title if available
    - Required technical skills
    - Required tools and frameworks
    - Important qualifications
    - Relevant responsibilities

    Return a concise analysis that another agent can use.
    Do not analyze the candidate yet.
""",
output_key="job_analysis",
)
