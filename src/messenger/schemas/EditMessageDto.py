from pydantic import BaseModel, Field


class EditMessageDto(BaseModel):
    content: str = Field(..., min_length=1, max_length=512, description="new content")
