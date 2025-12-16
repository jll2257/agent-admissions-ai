from __future__ import annotations
from typing import Dict, Any, List

from .base import AgentResult
from ..tools import tool_next_best_nudge

def run(db_path: str, session: Dict[str, Any], message: str, checklist_missing: List[str]) -> AgentResult:
    nudge = tool_next_best_nudge(session["segment"], checklist_missing)
    reply = (
        f"{nudge['message']}\n\n"
        "If you tell me your available time this week (e.g., 30–60 min blocks), I’ll map it to a simple plan."
    )
    return AgentResult(reply=reply, actions=[{"tool":"next_best_nudge","output":nudge}], citations=[])
