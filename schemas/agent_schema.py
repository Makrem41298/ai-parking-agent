from pydantic import BaseModel

class AgentRequest(BaseModel):
    question: str
    userId: int
    generationResponse:bool
    generalResponse:bool
