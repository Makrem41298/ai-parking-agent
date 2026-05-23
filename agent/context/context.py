from typing import TypedDict, Optional

from schemas.user_schemas import Role


class Context(TypedDict):
    mode_response: Optional[str]
    user_id: Optional[int]
    roleUser: Optional[Role]
    number_vectors: Optional[int]
