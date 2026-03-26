from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from .db_schemes import DataChunk
from bson.objectid import ObjectId
from typing import List
from pymongo import InsertOne


class DataChunkModel(BaseDataModel):
    def __init__(self, db_clinet):
        super().__init__(db_clinet)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_DATACHUNK_NAME.value]


    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True,exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk
    
    async def insert_many_chunks(self, chunks: list, batch_size:int=100):
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]
            print(batch)
            operations = [InsertOne(chunk.dict(by_alias=True,exclude_unset=True)) for chunk in batch]
            await self.collection.bulk_write(operations)

        return len(chunks)
    


    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one({
            '_id': ObjectId(chunk_id)
        })
        if result is None:
            return None
        return DataChunk(**result)


    async def delete_chunks_by_project_id(self, project_id:ObjectId):
        result =  await self.collection.delete_many({
            'project_id': project_id
        })
        return result.deleted_count

    