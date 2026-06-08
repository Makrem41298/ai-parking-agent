from typing import List, Any

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from schemas.user_schemas import Role


class AgentState(BaseModel):
    question: str
    messages: List[BaseMessage] = Field(default_factory=list)
    documents: List[Document] = Field(default_factory=list)
    mode_response: str | None = None
    user_id: int | None = None
    roleUser: Role | None = None
    reclamation_id: int | None = None
    session_id: str | None = None
    number_vectors: int | None = None
    answer: str | None = None