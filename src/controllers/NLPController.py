from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
import json
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, vector_db_client, embedding_client, generation_client):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client


    def create_collection(self, project_id: str):
        return f"collection_{project_id}".strip()
    

    def reset_vector_db_collection(self,project: Project ):
        collection_name = self.create_collection(project_id=project.project_id)
        return self.vector_db_client.delete_collection(collection_name=collection_name)
    

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection(project_id=project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vecto_db(self, project: Project, chunks: List[DataChunk], chunk_ids: List[int], do_reset: bool=False):
        collection_name = self.create_collection(project.project_id)
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = [self.embedding_client.generate_embedding(text, document_type=DocumentTypeEnum.DOCUMENT.value)
                            for text in texts]
        _ = self.vector_db_client.create_collection(collection_name=collection_name,
                                                    embedding_size=self.embedding_client.embedding_size,
                                                    do_reset=do_reset)
        _ = self.vector_db_client.insert_many(collection_name=collection_name,
                                              texts=texts,
                                              vectors=vectors,
                                              metadata=metadatas)
        return True

    def search_vector_db_collection(self, project: Project, query: str, limit:int=5):
        collection_name = self.create_collection(project_id=project.project_id)
        vector = self.embedding_client.generate_embedding(query, DocumentTypeEnum.QUERY.value)
        if not vector or len(vector) == 0:
            return False
        
        results = self.vector_db_client.search_by_vector(collection_name=collection_name,
                                                         vector=vector,
                                                         limit=limit)
        if not results:
            return False
        return results


    
