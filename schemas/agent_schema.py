from enum import Enum

from pydantic import BaseModel



class ModeResponse(str, Enum):
    user_response="user_response"
    general_response="general_response"
    reclamation_response="reclamation_response"
class AgentRequest(BaseModel):
    question: str
    userId: int
    reclamationId:int
    mode_response:ModeResponse
