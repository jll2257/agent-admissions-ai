from __future__ import annotations
from typing import List, Dict, Optional

# This demo ships with a deterministic MockLLM so it runs without keys or model downloads.
# You can plug in a real provider by implementing `generate()`.

class LLMClient:
    def __init__(self, provider: str = "mock"):
        self.provider = provider.lower()
        if self.provider != "mock":
            raise ValueError("Only 'mock' provider is enabled in this offline demo.")

    def generate(self, system: str, user: str, context: Optional[str] = None) -> str:
        # Deterministic mock responses so the demo runs without keys or model downloads.
        # If context is provided (RAG), we lightly summarize it to appear grounded.
        u = (user or "").lower()

        if context:
            # Pull a few informative lines from the retrieved context.
            lines = []
            for ln in context.splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("["):
                    continue
                # Skip very short lines
                if len(ln) < 40:
                    continue
                lines.append(ln)
            lines = lines[:6]
            if lines:
                bullets = "\n".join([f"- {l}" for l in lines])
                return (
                    "Based on the official Columbia admissions pages indexed in this demo, here are the most relevant details:\n"
                    f"{bullets}\n\n"
                    "If you tell me which checklist item you’re working on, I can suggest the next concrete step to reach file completion."
                )
        if "complete" in u or "checklist" in u or "missing" in u:
            return ("Here’s what to do next: (1) review the file checklist, (2) prioritize missing items, "
                    "(3) set mini-deadlines and request recommenders today. I can help you track status.")
        if "essay" in u:
            return ("I can help you strengthen your essay by making it more specific: "
                    "pick 1–2 experiences, show concrete impact, and connect them to your program goals.")
        if "military" in u or "deployment" in u or "active" in u:
            return ("For active-duty applicants, we should build a deployment-aware plan: "
                    "front-load transcript and recommender requests, and use buffered mini-deadlines.")
        if "fee waiver" in u:
            return ("Fee waivers are usually available for eligible applicants; requirements vary. "
                    "If you share your constraints, I can outline the typical steps and suggest contacting admissions to confirm.")
        return ("Got it. I can help you take the next step: start with a small milestone today "
                "(e.g., fill profile + confirm recommenders), then we’ll keep the file moving with reminders.")
