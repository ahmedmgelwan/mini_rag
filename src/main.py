from fastapi import FastAPI
from helpers import get_settings
from routes.base import base_router
from routes.data import data_router
from routes.nlp import nlp_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm import LLMProviderFactory
from stores.vectordb import VectorDBFactory

app = FastAPI()
@app.on_event('startup')
async def startup_db_client():
    app_settings = get_settings()
    app.db_conn = AsyncIOMotorClient(app_settings.DB_URL)
    app.db_client = app.db_conn[app_settings.DB_NAME]

    llm_provider_factory = LLMProviderFactory(config=app_settings)

    app.generation_client = llm_provider_factory.create(provider=app_settings.GENERATION_BACKEND)
    app.generation_client.set_genration_model(app_settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(provider=app_settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
                                    model_id= app_settings.EMBEDDING_MODEL_ID,
                                    embedding_size= app_settings.EMBEDDING_MODEL_SIZE
                                )
    vector_db_factory = VectorDBFactory(config=app_settings)
    app.vector_db_client = vector_db_factory.create(provider=app_settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()
    
@app.on_event('shutdown')
async def shutdown_db_client():
    app.db_conn.close()
    app.vector_db_client.disconnect()
    
app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)
