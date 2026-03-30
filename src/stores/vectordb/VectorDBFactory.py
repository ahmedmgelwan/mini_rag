from .providers import QdrantDB
from .VectorDBEnums import VectorDBEnums
from helpers.config import Settings
from controllers.BaseController import BaseController

class VectorDBFactory:
    def __init__(self, config: Settings):
        self.config = config
        self.base_controller = BaseController()


    def create(self, provider):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDB(
                db_path= db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )

