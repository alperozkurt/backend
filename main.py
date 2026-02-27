from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
