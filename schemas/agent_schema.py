from pydantic import BaseModel

class AgentRequest(BaseModel):
    question: str

    userId: int
    reclamationId:int
    generationResponse:bool
    generalResponse:bool
