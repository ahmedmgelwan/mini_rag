from enum import Enum


class VectorDBEnums(Enum):
    QDRANT = 'QDRANT'
    PGVECTOR = 'PGVECTOR'


class DistanceMethodEnums(Enum):
    DOT = 'dot'
    COSINE = 'cosine'

class PGVectorTableSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'
    _PREFIX = 'pgvector'

class PGVectorDistanceMethodEnums(Enum):
    COSINE = 'vector_cosine_ops'
    DOT = 'vector_l2_ops'

class PGvectorIndexTypeEnums(Enum):
    HNSW = 'hnsw'
    IVFFLAT = 'ivfflat'