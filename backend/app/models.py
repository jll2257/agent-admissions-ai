from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict
from datetime import date

Segment = Literal["traditional", "transfer", "international", "active_duty"]

class SessionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    segment: Segment = "traditional"
    target_program: str = Field(..., min_length=2, max_length=128)
    deadline: Optional[date] = None
    # Optional: create session from a mock applicant profile (demo feature)
    applicant_number: Optional[str] = None

class Session(BaseModel):
    session_id: str
    name: str
    segment: Segment
    target_program: str
    deadline: Optional[date] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)

class Citation(BaseModel):
    doc_id: str
    title: str
    snippet: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    actions: List[Dict] = []
    citations: List[Citation] = []
    escalated_to_human: bool = False
