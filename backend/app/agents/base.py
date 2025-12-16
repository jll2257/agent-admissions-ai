from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AgentResult:
    reply: str
    actions: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
    escalated_to_human: bool = False
