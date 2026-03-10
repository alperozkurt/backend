from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .database import engine
from .models import Base
from .routers import users, financial, auth

app = FastAPI(title="GençCüzdan API", version="1.0.0")

Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(financial.router)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "GençCüzdan API", "version": "1.0.0"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/echo")
async def echo(msg: Message):
    return {"you_sent": msg.text}
