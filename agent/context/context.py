from typing import TypedDict, Optional


class Context(TypedDict):
    mode_response: Optional[str]
    user_id: Optional[int]
    number_vectors: Optional[int]