from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .database import engine
from .models import Base
from .routers import users

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(users.router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://10.0.2.2",
        "http://192.168.1.150",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/echo")
async def echo(msg: Message):
    return {"you_sent": msg.text}
