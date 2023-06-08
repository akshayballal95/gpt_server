
from fastapi import FastAPI
from langcorn import create_service
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.conversation import conversation

class Input(BaseModel):
    human_input: str

class Output(BaseModel):
    output: str

app=FastAPI()

@app.post("/conversation")
async def input(input: Input):
    output = Output(output=conversation(input.human_input))
    return output

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "https://www.akshaymakes.com",
    "https://akshaymakes.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)