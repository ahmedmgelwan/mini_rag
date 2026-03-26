from fastapi import FastAPI
from helpers import get_settings
from routes.base import base_router
from routes.data import data_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings

app = FastAPI()
@app.on_event('startup')
async def startup_db_client():
    app_settings = get_settings()
    app.db_conn = AsyncIOMotorClient(app_settings.DB_URL)
    app.db_client = app.db_conn[app_settings.DB_NAME]

@app.on_event('shutdown')
async def shutdown_db_client():
    app.db_conn.close()

app.include_router(base_router)
app.include_router(data_router)
