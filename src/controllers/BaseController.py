from helpers.config import get_settings
import os
import string
import random

class BaseController:
    def __init__(self):
        self.app_setings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir, 'assets/files')


    def genrate_random_key(self, size:int=10):
        return ''.join(
                random.choices(string.ascii_lowercase+string.digits,k=size)
            )
    
        