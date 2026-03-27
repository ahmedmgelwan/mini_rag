from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    chunk_text: str = Field(...,min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(...,gt=0)
    project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {"key":[
                ('project_id',1)
                ],
            "name": "chunk_project_id_idx_1",
            "unique": False
            }
        ]