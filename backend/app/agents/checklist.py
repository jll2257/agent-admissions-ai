from __future__ import annotations
from typing import Dict, Any, List

from .base import AgentResult
from ..tools import tool_get_checklist

DEFAULT_ITEMS = [
    "Application form",
    "Official transcripts",
    "Recommendations (2)",
    "Personal statement / essays",
    "Application fee or waiver"
]

def run(db_path: str, session: Dict[str, Any], message: str) -> AgentResult:
    # If no checklist exists yet, we keep it minimal; UI can also initialize items.
    current = tool_get_checklist(db_path, session["session_id"])["checklist"]
    existing_items = {c["item"] for c in current}
    missing_items = [i for i in DEFAULT_ITEMS if i not in existing_items]
    actions = [{"tool":"get_checklist","output": {"checklist": current}}]
    reply_lines = ["Here’s your current file checklist status:"]
    if not current:
        reply_lines.append("- No items tracked yet. Start with these defaults:")
        for i in DEFAULT_ITEMS:
            reply_lines.append(f"  - {i} (set to: missing)")
    else:
        for c in current:
            reply_lines.append(f"- {c['item']}: **{c['status']}**")
    if missing_items:
        reply_lines.append("\nIf you want, I can initialize missing default items as `missing` so we can track progress.")
    reply_lines.append("\nWhat’s the *next* item you want to tackle today?")
    return AgentResult(reply="\n".join(reply_lines), actions=actions, citations=[])
