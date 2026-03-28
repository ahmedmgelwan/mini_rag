from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import Optional
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    project_id: ObjectId = Field(...)
    asset_name: str = Field(..., min_length=1)
    asset_type: str = Field(..., min_length=1)
    asset_size: Optional[int] = Field(None, gt=0)
    created_at: datetime = Field(default=datetime.utcnow())

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [('project_id', 1)],
                "name": "project_id_idx_1",
                "unique": False
            },
            {
                "key": [('project_id', 1), ('asset_name',1)],
                "name": "project_id_asset_name_idx_1",
                "unique": True
            }

        ]
