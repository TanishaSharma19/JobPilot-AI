from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.6-flash"

profile_analyzer = Agent(
    name = "profile_analyzer",
    model = Gemini(
        model = MODEL,
        retry_options = types.HttpRetryOptions(attempts = 3),
    ),
    instruction = """
    You are the Candidate Profile Analyzer for JobPilot AI.

    Analyze the candidate profile.

    Extract:
    - Technical skills
    - Frameworks
    - Tools
    - Databases
    - Programming languages
    - Relevant project experience
    - Relevant professional experience

    Do not invent experience.
    Return a concise analysis that another agent can use.
""",
output_key="candidate_analysis",
)













