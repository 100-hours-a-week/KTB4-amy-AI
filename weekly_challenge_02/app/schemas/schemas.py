from pydantic import BaseModel


class Create_post(BaseModel):
    username : str
    title : str
    content : str

class Update_post(BaseModel):
    title: str
    content: str


class Create_comment(BaseModel):
    content : str
    username : str

class Update_comment(BaseModel):
    content : str