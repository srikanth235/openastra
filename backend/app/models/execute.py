from typing import Any

from pydantic import BaseModel


class HurlExecuteRequest(BaseModel):
    script: str


class HurlExecuteResponse(BaseModel):
    success: bool
    output: Any
    exit_code: int
    time: int
