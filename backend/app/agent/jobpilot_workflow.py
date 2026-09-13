from google.adk.agents import SequentialAgent

from app.agent.job_analyzer import job_analyzer
from app.agent.profile_analyzer import profile_analyzer
from app.agent.gap_analyzer import gap_analyzer
from app.agent.application_planner import application_planner

jobpilot_workflow = SequentialAgent(
    name = "jobpilot_workflow",
    sub_agents = [
        job_analyzer,
        profile_analyzer,
        gap_analyzer,
        application_planner,
    ],
)
