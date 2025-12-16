from __future__ import annotations
from typing import Dict, Any, List

from .base import AgentResult

def run(db_path: str, session: Dict[str, Any], message: str) -> AgentResult:
    # Motivational + ethical competitiveness coaching
    seg = session["segment"]
    extra = ""
    if seg == "active_duty":
        extra = (
            "\n\nActive-duty edge: your leadership and accountability are strong — "
            "we’ll translate them into clear *impact* statements and match them to program fit."
        )
    reply = (
        "Let’s strengthen competitiveness without overpromising:\n"
        "1) Pick 1–2 core themes (impact, curiosity, leadership).\n"
        "2) For each activity, write: role → action → measurable outcome.\n"
        "3) For essays, use *specific moments*, not general claims.\n"
        "4) Ask recommenders early and share your goals + résumé (don’t script them)."
        f"{extra}\n\n"
        "If you paste a short activity description or essay paragraph, I’ll help you refine it."
    )
    return AgentResult(reply=reply, actions=[], citations=[])
