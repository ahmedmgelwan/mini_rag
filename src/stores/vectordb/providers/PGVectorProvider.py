from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import (DistacneMethodEnums, PGVectorTableSchemeEnums,
                           PGVectorDistanceMethodEnums, PGvectorIndexTypeEnums)

import logging
from typing import List
from models.db_schemes import RetrivedDocument
from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import sessionmaker
import json


class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client: sessionmaker, default_vector_size:int = 786, 
                 distance_method:str= None, index_threshold:int=100):
        
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.distance_method = distance_method
        self.index_threshold = index_threshold
        self.table_prefix = PGVectorTableSchemeEnums._PREFIX.value

        self.logger = logging.getLogger('uvicorn')

        if self.distance_method == DistacneMethodEnums.COSINE.value:
            self.distance_method = PGVectorDistanceMethodEnums.COSINE.value
        elif self.distance_method == DistacneMethodEnums.DOT.value:
            self.distance_method = PGVectorDistanceMethodEnums.DOT.value
        self.default_index_name = lambda collection_name: f'{collection_name}_vector_idx'

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                create_ext_sql = sql_text('CREATE EXTENSION IF NOT EXISTS vector')
                await session.execute(create_ext_sql)
                await session.commit()

    def disconnect(self):
        pass

    
    async def is_collection_existed(self, collection_name: str, )-> bool:
        record = None
        async with self.db_client() as session:
            list_tbl = sql_text('SELECT * FROM pg_tables WHERE tablename LIKE :collection_name')
            result = await session.execute(list_tbl, {'collection_name': collection_name})
            record = result.scalar_one_or_none()

        return bool(record)
    
    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            list_tbl = sql_text('SELECT * FROM pg_tables WHERE tablename LIKE :prefix')
            result = await session.execute(list_tbl, {'prefix':self.table_prefix})
            records = result.scalars().all()
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            table_info_sql = sql_text('''
                                      SELECT  schemaname, tablename, tablespace, hasindexes
                                      FROM pg_tables
                                      WHERE tablename = :collection_name
                                      ''')
            count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
            table_info = await session.execute(table_info_sql, {'collection_name': collection_name})
            record_count = await session.execute(count_sql)
            table_data = table_info.fetchone()

            if not table_data:
                return None
            return {
                "table_info":{
                    "schemaname": table_data[0],
                    "tablename": table_data[1],
                    "tablespace": table_data[2],
                    "hasindexes": table_data[3]
                },
                "record_count": record_count.scalar_one(),

            }
    
    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f'Deleting collection: {collection_name}')
                delete_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(delete_sql)
                await session.commit()
        
        return True
    
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool= False) -> bool:
        if do_reset:
            await self.delete_collection(collection_name=collection_name)

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f'Creating collection: {collection_name}')

            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name}('
                        f'{PGVectorTableSchemeEnums.ID.value} BIGSERIAL PRIMARY KEY,'
                        f'{PGVectorTableSchemeEnums.TEXT.value} TEXT,'
                        f'{PGVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}),'
                        f'{PGVectorTableSchemeEnums.CHUNK_ID.value} INTEGER,'
                        f'{PGVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\','
                        f'FOREIGN KEY ({PGVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunks(chunk_id) )'
                    )
                    await session.execute(create_sql)
                    await session.commit()

            return True
        return False
    
    async def is_index_existed(self, collection_name: str):
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            check_idx_sql = sql_text('SELECT 1 FROM pg_indexes WHERE tablename = :collection_name AND indexname= :index_name')
            result = await session.execute(check_idx_sql,
                                     {'collection_name': collection_name, 'index_name': index_name})
            return bool(result.scalar_one_or_none())
        


    async def create_vector_index(self, collection_name:str, index_type: str= PGvectorIndexTypeEnums.HNSW.value):
        is_index_existed = await self.is_index_existed(collection_name)
        if is_index_existed:
            return False
        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                result = await session.execute(count_sql)
                records_count  = result.scalar_one()
                if records_count < self.index_threshold:
                    return False
                self.logger.info(f'START: creating index on collection {collection_name}.')
                index_name = self.default_index_name(collection_name)
                create_idx_sql = sql_text(f'CREATE INDEX {index_name} ON {collection_name}'
                                          f'USING {index_type} {PGVectorTableSchemeEnums.VECTOR.value} {self.distance_method}')
            
                await session.execute(create_idx_sql)
                await session.commit()
            self.logger.info(f'END:  creating index on collection {collection_name}.')
        return True
    

    async def reset_vector_index(self, collection_name: str, index_type: str=PGvectorIndexTypeEnums.HNSW.value):
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f'Removing index from {collection_name}')
                drop_idx_sql = sql_text(f'DROP INDEX IF EXISTS {index_name}')
                await session.execute(drop_idx_sql)

        return await self.create_vector_index(collection_name=collection_name, index_type=index_type)
    

    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict, record_id: str=None):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(f'Can not insert into not existed collection {collection_name}')
            return False
        if not record_id:
            self.logger.error(f'Can not insert new record without chunk_id {collection_name}')
            return False
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(f'INSERT INTO {collection_name}'
                                      f'({PGVectorTableSchemeEnums.TEXT.value},  {PGVectorTableSchemeEnums.VECTOR.value}, {PGVectorTableSchemeEnums.CHUNK_ID.value}, {PGVectorTableSchemeEnums.METADATA.value})'
                                      'VALUES(:text, :vector, :chunk_id, :metadata)')
                metadata = json.dumps(metadata, ensure_ascii=False) if metadata else '{}'
                await session.execute(insert_sql,{
                    'text': text,
                    'vector': '[' +', '.join(str(v) for v in vector) + ']',
                    'chunk_id': record_id,
                    'metadata': metadata
                })
                await session.commit()
        await self.create_vector_index(collection_name=collection_name)

    
    async def insert_many(self, collection_name: str, texts: list, vectors: list=None, metadata: list=None,record_ids: list=None, batch_size: int=50):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(f'Can not insert records into not existed collection {collection_name}')
            return False
        if not record_ids:
            self.logger.error('record_ids is None')
            return 
        

        if len(vectors) != len(record_ids):
            self.logger.error(f'Invalid data items for collection {collection_name}')
            return False
        
        if not metadata or len(metadata) == 0:
            metadata = [None] * len(texts)
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i: i+batch_size]
                    batch_vectors = vectors[i: i+batch_size]
                    batch_metadata = metadata[i: i+batch_size]
                    batch_record_ids = record_ids[i: i+batch_size]
                    values = []
                    for _text, _vector, _metadata, _record_id in zip(batch_texts, batch_vectors, batch_metadata, batch_record_ids):
                        metadata_json = json.dumps(_metadata, ensure_ascii=False) if _metadata else '{}'
                        values.append({
                            'text': _text,
                            'vector': '[' +', '.join(str(v) for v in _vector) + ']',
                            'chunk_id': _record_id,
                            'metadata': metadata_json
                        })
                    

                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name}'
                                        f'({PGVectorTableSchemeEnums.TEXT.value},  {PGVectorTableSchemeEnums.VECTOR.value}, {PGVectorTableSchemeEnums.CHUNK_ID.value}, {PGVectorTableSchemeEnums.METADATA.value})'
                                        'VALUES(:text, :vector, :chunk_id, :metadata)')
                    await session.execute(batch_insert_sql, values)
            await session.commit()
        await self.create_vector_index(collection_name)
        return True
    



    async def search_by_vector(self, collection_name: str, vector: list, limit:int=5):
        is_collection_existed = await self.is_collection_existed(collection_name)
        if not is_collection_existed:
            self.logger.error(f'Can not search in a non-existed collection {collection_name}')
            return False
        vector = '[' + ', '.join(str(v) for v in vector) + ']'
        async with self.db_client() as session:
            search_sql = sql_text(f'SELECT {PGVectorTableSchemeEnums.TEXT.value} as text, 1- ({PGVectorTableSchemeEnums.VECTOR.value} <=> :vector) as score '
                                  f'FROM {collection_name} '
                                  'ORDER BY score DESC '
                                  f'LIMIT {limit}')
            result = await session.execute(search_sql, {'vector':vector})
            records = result.fetchall()
            return [
                RetrivedDocument(
                    text=text, score= score
                ) 
                for text, score in records
            ]
