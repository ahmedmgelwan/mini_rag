from fastapi import FastAPI
from helpers import get_settings
from routes.base import base_router
from routes.data import data_router
from routes.nlp import nlp_router
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.llm import LLMProviderFactory, TemplateParser
from stores.vectordb import VectorDBFactory

app = FastAPI()
@app.on_event('startup')
async def startup_db_client():
    app_settings = get_settings()
    app.db_conn = f'postgresql+asyncpg://{app_settings.POSTGRES_USERNAME}:{app_settings.POSTGRES_PASSWORD}@{app_settings.POSTGRES_HOST}/{app_settings.POSTGRES_MAIN_DB}'
    app.db_engine = create_async_engine(app.db_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )
    llm_provider_factory = LLMProviderFactory(config=app_settings)

    app.generation_client = llm_provider_factory.create(provider=app_settings.GENERATION_BACKEND)
    app.generation_client.set_genration_model(app_settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(provider=app_settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
                                    model_id= app_settings.EMBEDDING_MODEL_ID,
                                    embedding_size= app_settings.EMBEDDING_MODEL_SIZE
                                )
    vector_db_factory = VectorDBFactory(config=app_settings, db_client=app.db_client)
    app.vector_db_client = vector_db_factory.create(provider=app_settings.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()
    app.template_parser = TemplateParser(
        language=app_settings.PRIMARY_LANG,
        default_languae=app_settings.DEFAULT_LANG
    )
    
@app.on_event('shutdown')
async def shutdown_db_client():
    await app.db_engine.dispose()
    app.vector_db_client.disconnect()
    
app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)
