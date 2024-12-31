from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

