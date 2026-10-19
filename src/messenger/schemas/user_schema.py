from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import datetime
from typing import Literal, Optional
import re


GenderType = Literal["Male", "Female", "Prefer not to say"]


class UserDto(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8)
    birth_date: datetime
    phone: PhoneNumber | None = None
    name: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=200)
    gender: GenderType = "Prefer not to say"

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")

        return value
