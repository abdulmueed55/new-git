import os, json, re
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NEXA AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-chief-of-staff-fyp.onrender.com",
        "http://localhost:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class EmailRequest(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str

class AskRequest(BaseModel):
    question: str
    emails: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

async def gemini_json(prompt: str) -> dict:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key is not configured on the server.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }
    headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, headers=headers, json=payload)
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {r.text[:500]}")
    try:
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except Exception:
        raise HTTPException(status_code=502, detail="Gemini returned an invalid structured response.")

@app.get("/")
def root():
    return {"name": "NEXA AI API", "status": "ok", "gemini_configured": bool(GEMINI_API_KEY), "model": MODEL}

@app.get("/health")
def health():
    return {"status": "ok", "gemini_configured": bool(GEMINI_API_KEY), "model": MODEL}

@app.post("/analyze-email")
async def analyze_email(req: EmailRequest):
    prompt = f"""
You are the intelligence layer for NEXA, an AI Chief of Staff.
Analyze this email for a productivity assistant.

Sender: {req.sender}
Subject: {req.subject}
Body:
{req.body}

Return ONLY valid JSON with exactly these fields:
{{
  "summary": "one short sentence",
  "importance": "High|Medium|Low",
  "needs_reply": true,
  "task": "action item or empty string",
  "deadline": "natural-language deadline or empty string",
  "category": "Academic|Work|Meeting|Administrative|Personal|Promotional|Other",
  "reason": "brief explanation",
  "confidence": 0.0
}}
confidence must be between 0 and 1.
"""
    data = await gemini_json(prompt)
    return data

@app.post("/ask")
async def ask(req: AskRequest):
    context = {
        "emails": req.emails[:20],
        "tasks": req.tasks[:20],
        "events": req.events[:20],
    }
    prompt = f"""
You are NEXA, an AI Chief of Staff. Use ONLY the supplied user context.
Give a concise, actionable answer and explain the evidence.

USER QUESTION:
{req.question}

CONTEXT JSON:
{json.dumps(context, ensure_ascii=False)}

Return ONLY JSON:
{{
  "answer": "direct answer",
  "next_actions": ["action 1", "action 2"],
  "evidence": ["evidence item 1", "evidence item 2"],
  "risk": "one short risk/constraint or empty string"
}}
"""
    return await gemini_json(prompt)
