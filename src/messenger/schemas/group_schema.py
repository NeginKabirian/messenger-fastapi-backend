from pydantic import BaseModel, Field
from typing import Optional, List


class CreateGroupDto(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None


class AddMemberDto(BaseModel):
    users_ids: List[str]


class sendGroupMessageDto(BaseModel):
    content: str
