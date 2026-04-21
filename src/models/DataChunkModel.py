from .BaseDataModel import BaseDataModel
from .enums import DatabaseEnum
from .db_schemes import DataChunk
from sqlalchemy.future import select
from sqlalchemy import func, delete

class DataChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)

    @classmethod
    async def create_instance(cls,db_client):
        instance = cls(db_client)
        return instance


    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        
        return chunk
    
    async def insert_many_chunks(self, chunks: list, batch_size:int=100):
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0,len(chunks),batch_size):
                    batch = chunks[i:i+batch_size]
                    session.add_all(batch)
            await session.commit()

        return len(chunks)
    


    async def get_chunk(self,chunk_id:str):
        chunk_id = int(chunk_id)
        async with self.db_client() as session:
            chunk =  await session.execute(
                        select(DataChunk).where(DataChunk.chunk_id == chunk_id)
                    )
            chunk = chunk.scalar_one_or_none()
            return chunk

    async def delete_chunks_by_project_id(self, project_id:str):
        project_id = int(project_id)
        async with self.db_client() as session:
            async with session.begin():
                query = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
                result = await session.execute(query)
            result = result.rowcount
        return result    
    
    async def get_project_chunks(self, project_id: str, page_no: int=1, page_size: int =50):
        project_id = int(project_id)
        async with self.db_client() as session:
            query = select(DataChunk).where(
                            DataChunk.chunk_project_id == project_id
                            ).offset((page_no-1) * page_size).limit(page_size)
            chunks = await session.execute(query)
            chunks = chunks.scalars().all()
        return chunks

    