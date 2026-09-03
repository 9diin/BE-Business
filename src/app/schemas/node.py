from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CreateNodeRequest(BaseModel):
    title: str
    description: str
    category: str
    user_id: str


class UpdateNodeRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None


class NodeResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)