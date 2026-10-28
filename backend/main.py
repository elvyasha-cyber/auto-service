from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db import init_tables
from routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_tables()
    yield


app = FastAPI(
    title="Auto Service API",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(api_router)
