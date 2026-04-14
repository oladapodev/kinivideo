from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from config import settings


app = FastAPI(title=settings.app_name, docs_url=settings.docs_url)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
