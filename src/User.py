from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr , Field
from pydantic_extra_types.phone_numbers import PhoneNumber

GenderType = Literal["Male", "Female", "Prefer not to say"]
class User(BaseModel):
    
    id:int | None = None
    username: str 
    email:EmailStr
    hashed_password: str
    birth_date:datetime 
    phone: PhoneNumber | None = None
    name: str = ""
    bio: str | None = None
    last_seen: datetime | None = None
    
    is_logged_in: bool = False
    signup_ts: datetime = Field(default_factory=datetime.now)
    gender: GenderType= "Prefer not to say"