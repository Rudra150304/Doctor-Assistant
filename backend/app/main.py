# doctor-assistant/backend/app/main.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from .agent import run_agent
from .auth import router as auth_router

from .notifications import get_notifications

app = FastAPI()

app.include_router(auth_router)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- SESSION STORE ----------------
sessions: Dict[str, Dict] = {}


def get_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "context": {}
        }
    return sessions[session_id]

#------------------ Notifications----------------
@app.get("/notifications/{doctor_id}")
def fetch_notifications(doctor_id: int):
    return get_notifications(doctor_id)


# ---------------- CHAT ENDPOINT ----------------
@app.post("/chat")
def chat(
    message: str = Query(...),
    session_id: str = Query(...),
    name: str = Query(None),
    email: str = Query(None)
):
    session = get_session(session_id)

    # Store user message
    session["messages"].append({
        "role": "user",
        "content": message
    })

    # Store patient info (optional)
    if name and email:
        session["context"]["patient"] = {
            "name": name,
            "email": email
        }

    # Run agent
    response = run_agent(session["messages"], session["context"])

    # Store assistant response
    session["messages"].append({
        "role": "assistant",
        "content": response
    })

    return {"response": response}


# ---------------- HEALTH CHECK ----------------
@app.get("/")
def root():
    return {"status": "ok"}
