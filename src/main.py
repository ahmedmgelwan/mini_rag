from fastapi import FastAPI
from helpers import get_settings
from routes.base import base_router
from routes.data import data_router


app = FastAPI()

app.include_router(base_router)
app.include_router(data_router)
