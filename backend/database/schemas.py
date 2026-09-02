from pydantic import BaseModel
from typing import List, Optional

class UserJoin(BaseModel):
    session_id: str
    name: str
    group_code: str

class GroupCreate(BaseModel):
    session_id: str

class PreferenceCreate(BaseModel):
    session_id: str
    destination_type: str
    budget: float

class VoteCreate(BaseModel):
    session_id: str
    destination_name: str

class GroupResponse(BaseModel):
    group_code: str
    is_host: bool
    recommendations_generated: bool
    users: List[dict]
    pooled_budget: float
    recommendations: List[dict]
    adk_insights: str
    votes: dict
