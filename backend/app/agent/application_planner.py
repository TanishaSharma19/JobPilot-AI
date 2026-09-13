from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.schemas import JobAnalysisResult

MODEL = "gemini-3.6-flash"

application_planner = Agent(
    name = "application_planner",
    model = Gemini(
        model = MODEL,
        retry_options = types.HttpRetryOptions(attempts = 3),
    ),
    instruction = """
    You are the final Application Planner for JobPilot AI.
    Use the results from the previous workflow steps.

    JOB ANALYSIS:
    {job_analysis}

    CANDIDATE ANALYSIS:
    {candidate_analysis}

    SKILL GAP ANALYSIS:
    {skill_gap_analysis}

    Create the final JobPilot analysis.

    Determine:
    - Overall match score from 0 to 100
    - Important job requirements
    - Candidate's strongest matching skills
    - Important skill gaps
    - Concrete prioritized action plan
    - Personalized application advice

    Do not invent candidate experience.
    Only use evidence from the provided job and candidate information.
""",
    output_schema = JobAnalysisResult,
    output_key="application_plan",
)
