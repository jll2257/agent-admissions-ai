from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime, date

from .base import AgentResult
from ..tools import tool_deployment_buffer

def _parse_date(text: str) -> Optional[date]:
    try:
        return datetime.fromisoformat(text.strip()).date()
    except Exception:
        return None

def run(db_path: str, session: Dict[str, Any], message: str) -> AgentResult:
    # Look for a deployment date in ISO format in the message, e.g., 2025-10-15
    dep = None
    for token in message.split():
        d = _parse_date(token)
        if d:
            dep = d
            break
    deadline = None
    if session.get("deadline"):
        try:
            deadline = datetime.fromisoformat(session["deadline"]).date()
        except Exception:
            deadline = None
    plan = tool_deployment_buffer(deadline=deadline, deployment_start=dep)
    reply = (
        "Military support plan (deployment-aware):\n"
        "- Front-load transcript and recommender requests\n"
        "- Set mini-deadlines and keep a ‘soft deadline’ buffer\n"
        "- Prepare a concise service-to-impact translation for activities\n"
        "\nIf you share a deployment start date (YYYY-MM-DD), I’ll compute a buffered timeline."
    )
    return AgentResult(reply=reply, actions=[{"tool":"deployment_buffer","output":plan}], citations=[])
