from pydantic import BaseModel


class CreateNodeRequest(BaseModel):
    title: str
    description: str
    category: str

class UpdateNodeRequest(BaseModel):
    title: str | None
    description: str | None 
    category: str | None   