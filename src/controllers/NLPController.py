from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
import json
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.llm import TemplateParser


class NLPController(BaseController):
    def __init__(self, vector_db_client, embedding_client, generation_client, template_parser: TemplateParser):
        super().__init__()
        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser



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


    def answer_rag_question(self, project: Project, query: str, limit:int=5):
        answer, full_prompt, chat_history = None, None, None
        
        retreved_documents = self.search_vector_db_collection(project,query, limit)
        if not retreved_documents or len(retreved_documents) == 0:
            return None
        
        system_prompt = self.template_parser.get("rag", "system_prompt")
        document_prompt = "\n".join([self.template_parser.get('rag',"document_prompt",
                                    vars={
                                            "doc_num": i+1,
                                            "chunk_text": doc.text
                                        }) 
                                        for i,doc in enumerate(retreved_documents)])
        footer_prompt = self.template_parser.get('rag','footer_prompt',
                                                 vars={'query':query})
        
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,

            )
        ]
        full_prompt = '\n\n'.join([document_prompt, footer_prompt])
        answer = self.generation_client.generate_text(
            prompt = full_prompt,
            chat_history=chat_history
        )
        return answer, full_prompt, chat_history
