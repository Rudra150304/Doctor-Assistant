# doctor-assistant/backend/app/main.py

from fastapi import FastAPI, Body
from .agent import run_agent
from .db import Base, engine
from .seed import run_seed
from .auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from .notifications import get_notifications

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

sessions = {}

@app.on_event("startup")
def startup():
    run_seed()

@app.get("/notifications/{doctor_id}")
def fetch_notifications(doctor_id: int):
    return get_notifications(doctor_id)

@app.post("/chat")
def chat(session_id: str, message: str, name: str = None, email: str = None):

    # ---------------- Session Init ----------------
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "context": {}
        }

    session = sessions[session_id]

    # ---------------- Store Patient Context ----------------
    if name and email:
        session.setdefault("context", {})
        session["context"]["patient"] = {
            "name": name,
            "email": email
        }

    # ---------------- Extract Doctor ----------------
    doctor_id = None
    role = "patient"

    if session_id.startswith("doc_"):
        try:
            doctor_id = int(session_id.split("_")[1])
            role = "doctor"
        except:
            pass

    # ---------------- Add User Message ----------------
    session["messages"].append({
        "role": "user",
        "content": message
    })

    # ---------------- Run Agent ----------------
    response = run_agent(
        session=session,
        doctor_id=doctor_id,
        role=role
    )

    # ---------------- Save Response ----------------
    session["messages"].append({
        "role": "assistant",
        "content": response
    })

    return {"response": response}
