from fastapi import FastAPI
from helpers import get_settings
from routes.base import base_router


app = FastAPI()

app.include_router(base_router)
