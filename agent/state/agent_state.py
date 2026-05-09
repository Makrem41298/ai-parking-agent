from typing import List, Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    question: str
    messages: List[BaseMessage] = Field(default_factory=list)
    answer: str | None = None