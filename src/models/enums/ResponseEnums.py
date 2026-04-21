from enum import Enum

class ResponseSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FIEL_SIZE_EXCEEED_MAXIMUM = 'file_size_exceed_maximum_size'
    FILE_UPLODED_SUCESS = 'file_uploaded_success'
    FILE_UPLOADED_FAIL = 'file_uploaded_failed'
    FILE_PROCESSING_SUCCESS = 'file_processing_success'
    FILE_PROCESSING_FAIL = 'file_processing_failed'
    FILE_ID_ERROR = 'file_id_error'
    NO_FILES_ERROR = 'no_files_with_this_project'
    PROJECT_NOT_FOUND_ERROR = 'project_not_found'
    INSERT_INTO_VECTOR_DB_ERROR = 'insert_into_vectordb_error'
    INSERT_INTO_VECTOR_DB_SUCCESS = 'insert_into_vectordb_success'
    VECTOR_DB_COLLECTION_INFO_RETEIVED = 'collection_info_reteived'
    VECTOR_DB_SEARCH_ERROR = "vector_db_search_error"
    VECTOR_DB_SEARCH_SUCCESS = "vector_db_search_success"
    RAG_ANSWER_ERROR = 'rag_answer_error'
    RAG_ANSWER_SUCCESS = 'rag_answer_success'