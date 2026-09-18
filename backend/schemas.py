from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str
    last_name: str
    email: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class FavoriteBase(BaseModel):
    pokemon_name: str
    pokemon_data: str

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
