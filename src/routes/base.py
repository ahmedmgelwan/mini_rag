from fastapi import FastAPI, APIRouter
from helpers.config import get_settings


base_router = APIRouter(
    prefix="/api/v1",
    tags=['v1']
)

@base_router.get('/')
def welcome():
    app_settings = get_settings()
    return {
        'App Name': app_settings.APP_NAME,
        'App Version': app_settings.APP_VERSION
    }

