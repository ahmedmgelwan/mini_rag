from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings


base_router = APIRouter(
    prefix="/api/v1",
    tags=['v1']
)

@base_router.get('/')
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        'App Name': app_settings.APP_NAME,
        'App Version': app_settings.APP_VERSION
    }

