from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

gap_analyzer = Agent(
    name = "gap_analyzer",
    model = Gemini(
        model = MODEL,
        retry_options = types.HttpRetryOptions(attempts = 3),
    ),
    instruction ="""
    You are the Skill Gap Analyzer for JobPilot AI.

    Compare the job requirements with the candidate's skills and experience.

    Identify:
    - Skills the candidate already has
    - Skills that are missing
    - Skills that are weak or insufficiently demonstrated
    - Priority of each gap: High, Medium, or Low
    - Why each gap matters for the target role

    Do not invent candidate skills or experience.

    Return a concise skill-gap analysis that another agent can use.
""",
output_key="skill_gap_analysis",
)
