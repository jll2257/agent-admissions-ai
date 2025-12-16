from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, timedelta

from .config import settings
from .db import upsert_checklist_item, get_checklist

def tool_update_checklist(db_path: str, session_id: str, item: str, status: str) -> Dict[str, Any]:
    status = status.lower().strip()
    if status not in {"missing","in_progress","submitted","verified"}:
        raise ValueError("Invalid status. Use one of: missing, in_progress, submitted, verified.")
    upsert_checklist_item(db_path, session_id, item.strip(), status)
    return {"ok": True, "item": item, "status": status}

def tool_get_checklist(db_path: str, session_id: str) -> Dict[str, Any]:
    return {"checklist": get_checklist(db_path, session_id)}

def tool_deployment_buffer(deadline: Optional[date], deployment_start: Optional[date]) -> Dict[str, Any]:
    if not deadline or not deployment_start:
        return {"note": "Provide both a deadline and deployment_start to compute a buffered plan."}
    # Simple heuristic: create a “soft deadline” 14 days before deployment starts, if deployment is before deadline.
    soft = deadline
    if deployment_start <= deadline:
        soft = deployment_start - timedelta(days=14)
    return {"deadline": deadline.isoformat(), "deployment_start": deployment_start.isoformat(), "soft_deadline": soft.isoformat()}

def tool_next_best_nudge(segment: str, missing_items: List[str]) -> Dict[str, Any]:
    if not missing_items:
        return {"message": "Nice work — your file looks complete. Consider polishing your essays and preparing for any interview steps."}
    item = missing_items[0]
    if segment == "active_duty":
        return {"message": f"Next best step: focus on '{item}'. If your schedule is tight, we can plan a mini-deadline and alternate submission route."}
    return {"message": f"Next best step: complete '{item}'. A small milestone today keeps the file moving."}
