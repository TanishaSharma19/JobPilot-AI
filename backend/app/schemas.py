from pydantic import BaseModel
from typing import List

class JobAnalysisResult(BaseModel):
    match_score: int
    job_requirements: List[str]    
    strong_matches : List[str]
    skill_gaps: List[str]
    action_plan : List[str]
    application_advice : str
