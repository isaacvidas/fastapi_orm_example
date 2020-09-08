from typing import List

from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    owner_id: int
    description: str = None

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    email: str
    is_active: bool
    # items: List[Item] = [] # Uncomment this to simulate N+1

    class Config:
        orm_mode = True
