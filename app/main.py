
from fastapi import FastAPI
from langcorn import create_service
from fastapi.middleware.cors import CORSMiddleware



app:FastAPI = create_service("app.conversation:conversation_chain")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "https://www.akshaymakes.com",
    "https://akshaymakes.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)