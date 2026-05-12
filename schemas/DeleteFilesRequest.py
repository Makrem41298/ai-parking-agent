from typing import List

from pydantic import BaseModel


class DeleteFilesRequest(BaseModel):
    filenames: List[str]