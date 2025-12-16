from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

HIGH_STAKES_TRIGGERS = [
    "legal", "lawsuit", "medical", "diagnosis", "disability",
    "criminal", "felony", "misdemeanor", "court", "immigration",
    "should i lie", "fake", "fabricate", "cheat", "forge"
]

@dataclass
class PolicyDecision:
    escalated_to_human: bool
    reason: str = ""

def should_escalate(user_text: str) -> PolicyDecision:
    t = user_text.lower()
    for k in HIGH_STAKES_TRIGGERS:
        if k in t:
            return PolicyDecision(True, f"High-stakes or integrity-related query trigger: '{k}'")
    return PolicyDecision(False, "")

def enforce_no_guarantees(reply: str) -> str:
    # Guardrail: avoid absolute guarantees or admissions predictions.
    banned = ["guarantee", "certainly admitted", "will be admitted", "100%"]
    out = reply
    for b in banned:
        out = out.replace(b, "cannot guarantee")
    return out
