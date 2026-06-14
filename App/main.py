from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
from App.redis_client import get_history, save_history, clear_session
from App.groq_client import chat_with_groq

from typing import Optional


print(f"Handled by process: {os.getpid()}")

app = FastAPI(title="Redis Chatbot")


class ChatRequest(BaseModel):
    session_id: Optional[str] = None  # None = start new session
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history_length: int


import os

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Load history from Redis
    history = await get_history(session_id)

    # ADD THIS LINE 👇
    print(f"[PID {os.getpid()}] Session: {session_id} | History length: {len(history)}")

    # Append the new user message
    history.append({"role": "user", "content": req.message})

    try:
        reply = chat_with_groq(history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    history.append({"role": "assistant", "content": reply})
    await save_history(session_id, history)

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        history_length=len(history),
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    await clear_session(session_id)
    return {"message": f"Session {session_id} cleared."}


@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    history = await get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": history}


@app.get("/")
async def root():
    return {"message": "Redis Chatbot is running. POST to /chat to start."}