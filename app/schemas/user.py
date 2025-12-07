from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    id: int
    identifier: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
