from enum import Enum
from typing import Optional
from pydantic import BaseModel
from schemas.user_schemas import Role


class ModeResponse(str, Enum):
    user_response="user_response"
    general_response="general_response"
    reclamation_response="reclamation_response"
class AgentRequest(BaseModel):
    question: str
    userId: Optional[int]=None
    roleUser: Optional[Role] = None
    reclamationId:Optional[int]=None
    sessionId:Optional[str]=None
    mode_response:ModeResponse
