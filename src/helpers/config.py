from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_UPLOADED_MAXIMUM_SIZE: int
    FILE_UPLOADED_ALLOWED_TYPES: list
    FILE_DEFUALT_CHUNK_SIZE: int
    DB_URL: str
    DB_NAME: str
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    COHERE_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    INPUT_DAFAULT_MAX_CHARACTERS: int
    GENERATION_DAFAULT_MAX_TOKENS: int
    GENERATION_DAFAULT_TEMPERATURE: float

    class Config:
        env_file= '.env'

def get_settings():
    return Settings()