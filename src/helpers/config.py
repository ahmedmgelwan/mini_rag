from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_UPLOADED_MAXIMUM_SIZE: int
    FILE_UPLOADED_ALLOWED_TYPES: list
    FILE_DEFUALT_CHUNK_SIZE: int

    class Config:
        env_file= '.env'

def get_settings():
    return Settings()