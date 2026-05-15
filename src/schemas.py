from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Post(BaseModel):
    title: str
    content: str
    #author: str  # we'll link this to a real user later
    image_url: Optional[str] = None  # optional field for image URL

class UserLogin(BaseModel):
    username: str
    password: str
    #author: str