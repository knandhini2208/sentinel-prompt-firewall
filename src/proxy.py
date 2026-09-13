import os
import time
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from db import get_connection
from scoring import score_prompt

load_dotenv()

app = FastAPI(title="Sentinel Prompt Firewall")


class ChatRequest(BaseModel):
    session_id: str
    prompt: str


def call_llm(prompt: str) -> str:
    """Stub LLM call. Swap this out for a real API (OpenAI, Anthropic, etc.)
    using LLM_PROVIDER / LLM_API_KEY from .env."""
    provider = os.environ.get("LLM_PROVIDER", "stub")
    if provider == "stub":
        return f"[stub response] I received: {prompt[:80]}"
    raise NotImplementedError(f"Wire up provider '{provider}' in call_llm().")


def log_to_exasol(session_id, prompt, response, result, latency_ms):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO SENTINEL.AUDIT_LOG
            (SESSION_ID, TS, PROMPT, RESPONSE, HEURISTIC_SCORE,
             SIMILARITY_SCORE, MATCHED_CATEGORY, DECISION, LATENCY_MS)
        VALUES ({session_id}, {ts}, {prompt}, {response}, {heuristic_score},
                {similarity_score}, {matched_category}, {decision}, {latency_ms})
        """,
        {
            "session_id": session_id,
            "ts": datetime.utcnow(),
            "prompt": prompt,
            "response": response,
            "heuristic_score": result["heuristic_score"],
            "similarity_score": result["similarity_score"],
            "matched_category": result["matched_category"],
            "decision": result["decision"],
            "latency_ms": latency_ms,
        },
    )


@app.post("/chat")
def chat(req: ChatRequest):
    start = time.time()
    result = score_prompt(req.prompt)

    if result["decision"] == "BLOCK":
        response_text = "This request was blocked by Sentinel's safety filter."
    else:
        # FLAG still gets forwarded in this MVP; block only stops execution.
        response_text = call_llm(req.prompt)

    latency_ms = int((time.time() - start) * 1000)
    log_to_exasol(req.session_id, req.prompt, response_text, result, latency_ms)

    return {
        "response": response_text,
        "decision": result["decision"],
        "matched_category": result["matched_category"],
        "heuristic_score": result["heuristic_score"],
        "similarity_score": result["similarity_score"],
        "latency_ms": latency_ms,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
