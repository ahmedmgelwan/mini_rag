from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models.enums import ProcessingEnum
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_dir(project_id)

    def get_file_ext(self, file_id):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self,file_id):
        file_ext = self.get_file_ext(file_id)
        file_path = os.path.join(
            self.project_path, file_id
        )
        if file_ext == ProcessingEnum.TXT.value:
            loader = TextLoader(file_path=file_path,encoding='utf-8')
        if file_ext == ProcessingEnum.PDF.value:
            loader = PyMuPDFLoader(file_path=file_path)

        return loader
    
    def get_file_content(self,file_id):
        loader = self.get_file_loader(file_id)
        return loader.load()
    
    def process_file_content(self, file_id:str, file_content: list, chunk_size: int = 100, overlap_size: int = 20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_size)
        file_content_text = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]

        return text_splitter.create_documents(
                                                texts=file_content_text,
                                                metadatas=file_content_metadata
                                            )   
        
    
