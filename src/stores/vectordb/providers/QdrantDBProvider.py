from ..VectorDBInterface import VectorDBInterface
from qdrant_client import models, QdrantClient
from ..VectorDBEnums import DistacneMethodEnums
from typing import List 
import logging
from models.db_schemes.mini_rag.schemes import RetrivedDocument

class QdrantDB(VectorDBInterface):
    def __init__(self, db_client: str, default_vector_size:int = 786, 
                 distance_method:str= None, index_threshold:int=100):
        self.db_client = db_client
        self.distance_method = None
        if distance_method == DistacneMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        elif distance_method == DistacneMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE

        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    def disconnect(self):
        self.client = None

    async def is_collection_existed(self, collection_name: str, )-> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    async def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name)
    
    async def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool= False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name=collection_name):
            return self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method)
                        
            )
        return False
    
    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict, record_id: str=None):
        if not self.is_collection_existed(collection_name):
            self.logger.error(f'Can not insert record to non-existed collection: {collection_name}')
            return False
        _ = self.client.upload_records(
                                        collection_name=collection_name,
                                        records=[
                                            models.Record(
                                                vector=vector,
                                                payload={
                                                    'text': text,
                                                    'metadata': metadata
                                                }
                                            )
                                        ]
                                    )
        return True
    
    async def insert_many(self, collection_name: str, texts: list, vectors: list=None, metadata: list=None,record_ids: list=None, batch_size: int=50):
        if not metadata:
            metadata = [None] * len(texts)
        
        if not record_ids:
            record_ids = list(range(0,len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size
            batch_text = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i: batch_end]

            batch_records = [models.Record(id=batch_record_ids[j],
                                            vector=batch_vectors[j],
                                            payload={'text': batch_text[j], 'metadata': batch_metadata[j]}
                                             )    for j in range(len(batch_text))]
            try:
                _ = self.client.upload_records(collection_name=collection_name, records = batch_records)
            except Exception as e:
                self.logger.error(f'Error while inserting batch {e}')
                return False
            
        return True
    
    async def search_by_vector(self, collection_name: str, vector: list, limit:int=5):
        results =  self.client.search(collection_name=collection_name, query_vector=vector, limit=limit)
        if not results or len(results) ==0:
            return None
        
        return [
            RetrivedDocument(
                **{
                        'text': result.payload['text'],
                        'score': result.score
                }
            ) for result in results
        ]
    
    
    

            



    
