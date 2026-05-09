from typing import List, Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    question: str
    messages: List[BaseMessage] = Field(default_factory=list)
    mode_response: str | None = None
    user_id: int | None = None
    reclamation_id: int | None = None
    answer: str | None = None