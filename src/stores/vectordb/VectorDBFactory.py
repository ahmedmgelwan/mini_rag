from .providers import QdrantDB, PGVectorProvider
from .VectorDBEnums import VectorDBEnums
from helpers.config import Settings
from controllers.BaseController import BaseController

class VectorDBFactory:
    def __init__(self, config: Settings, db_client=None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client


    def create(self, provider):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            return QdrantDB(
                db_client= db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        if provider == VectorDBEnums.PGVECTOR.value:
            return PGVectorProvider(db_client = self.db_client,
                                    default_vector_size = self.config.EMBEDDING_MODEL_SIZE,
                                    distance_method = self.config.VECTOR_DB_DISTANCE_METHOD, 
                                    index_threshold = self.config.VECTOR_DB_PGVEC_INDEX_THRESHOLD
            )
        
        return None

