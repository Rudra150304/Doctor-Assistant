#doctor-assistant/backend/app/main.py
from fastapi import FastAPI
from .agent import run_agent
from .db import Base, engine
from .seed import run_seed
from .mcp import TOOLS_MCP

app = FastAPI()

Base.metadata.create_all(bind=engine)

sessions = {}


@app.on_event("startup")
def startup():
    run_seed()


@app.get("/")
def root():
    return {"message": "Backend running 🚀"}


@app.get("/mcp/tools")
def get_mcp_tools():
    return TOOLS_MCP


@app.post("/chat")
def chat(session_id: str, message: str):
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({
        "role": "user",
        "content": message
    })

    response = run_agent(sessions[session_id])

    sessions[session_id].append({
        "role": "assistant",
        "content": response
    })

    return {"response": response}
