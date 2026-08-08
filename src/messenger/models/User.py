from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from uuid import uuid4

GenderType = Literal["Male", "Female", "Prefer not to say"]


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    username: str
    email: EmailStr
    hashed_password: str
    birth_date: datetime
    phone: PhoneNumber | None = None
    name: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=200)
    last_seen: datetime | None = None

    is_logged_in: bool = False
    signup_ts: datetime = Field(default_factory=datetime.now)
    gender: GenderType = "Prefer not to say"
