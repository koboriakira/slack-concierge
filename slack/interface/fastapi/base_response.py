from typing import Any

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    status: str = Field(default="SUCCESS")
    message: str = Field(default="")
    data: Any = Field(default=None)

    def __init__(self, status: str = "SUCCESS", message: str = "", data: Any = None) -> None:
        super().__init__(status=status, message=message, data=data)
