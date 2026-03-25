from enum import Enum

class ResposeSignal(Enum):
    FILE_TYPE_NOT_SUPPORTED = 'file_type_not_supported'
    FIEL_SIZE_EXCEEED_MAXIMUM = 'file_size_exceed_maximum_size'
    FILE_UPLODED_SUCESS = 'file_uploaded_success'
    FILE_UPLOADED_FAIL = 'file_uploaded_failed'
    