from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseSignal
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
    
    def validate_uploaded_file(self ,file:UploadFile):
        if file.content_type not in self.app_setings.FILE_UPLOADED_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_setings.FILE_UPLOADED_MAXIMUM_SIZE*1024*1024:
            return False, ResponseSignal.FIEL_SIZE_EXCEEED_MAXIMUM.value
        
        
        return True, ResponseSignal.FILE_UPLODED_SUCESS.value
    
    def generate_unique_file_path(self, project_id:str, file_name:str):
        clean_file_name = self.get_clean_file_name(file_name)
        random_key = self.genrate_random_key()
        project_dir = ProjectController().get_project_dir(project_id)
        new_file_path = os.path.join(project_dir,
                                     random_key + '_' + clean_file_name )
        while os.path.exists(new_file_path):
            random_key = self.genrate_random_key()
            new_file_path = os.path.join(self.files_dir,
                                        random_key + '_' + clean_file_name )
        return new_file_path, random_key + '_' + clean_file_name
    
    
    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name
        
