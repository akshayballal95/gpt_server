
from fastapi import FastAPI
from langcorn import create_service

app:FastAPI = create_service("app.conversation:conversation_chain")