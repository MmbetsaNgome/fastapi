from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title:str
    content:str
    published:bool = True

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime

    class Config:
        orm = True

class Post(PostBase):
    id:int
    created_at:datetime
    owner_id:int
    owner:UserOut

    class Config:
        orm = True


class Vote(BaseModel):
    post_id:int
    dir: Annotated[int, Field(strict=True, le=1)]


class PostOut(BaseModel):
    Post:Post
    votes:int

    class Config:
        orm = True
    

class UserCreate(BaseModel):
    email:EmailStr
    password:str



class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token:str 
    token_type:str

class TokenData(BaseModel):
    id : Optional[str] = None

