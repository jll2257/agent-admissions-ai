from __future__ import annotations
from typing import Dict, Any, List

from .base import AgentResult
from . import outreach, checklist, coach, military, rag_qa
from ..rag.retriever import TfidfRetriever
from ..llm import LLMClient
from ..db import get_checklist

def route(retriever: TfidfRetriever, llm: LLMClient, db_path: str, session: Dict[str, Any], message: str) -> AgentResult:
    t = message.lower()
    # basic intent routing
    if session["segment"] == "active_duty" and ("deployment" in t or "active duty" in t or "pcs" in t or "orders" in t):
        return military.run(db_path, session, message)
    if "checklist" in t or "complete" in t or "missing" in t or "documents" in t:
        return checklist.run(db_path, session, message)
    if "improve" in t or "competitive" in t or "essay" in t or "activities" in t:
        return coach.run(db_path, session, message)
    if "remind" in t or "nudge" in t or "next step" in t or "start" in t:
        cl = get_checklist(db_path, session["session_id"])
        missing = [c["item"] for c in cl if c["status"] in ("missing","in_progress")]
        return outreach.run(db_path, session, message, missing)
    # default: RAG Q&A
    return rag_qa.run(retriever, llm, session, message)
