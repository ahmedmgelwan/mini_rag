from helpers.config import get_settings

class BaseDataModel:
    def __init__(self,db_clinet:object):
        self.db_client = db_clinet
        self.app_settings = get_settings()