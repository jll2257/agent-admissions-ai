"""Reproducible evaluation script (lightweight, offline).

We simulate a small cohort of applicants with randomized missing checklist items and
measure whether the agent:
  - returns a concrete next step,
  - provides citations when doing policy/FAQ Q&A,
  - escalates on integrity/high-stakes prompts.
"""
import json
import random
from pathlib import Path

from backend.app.rag.retriever import TfidfRetriever
from backend.app.llm import LLMClient
from backend.app.agents.router import route
from backend.app.config import settings
from backend.app.db import init_db, create_session, get_session, upsert_checklist_item
from backend.app.policies import should_escalate

OUT_JSON = Path("experiments/results.json")
OUT_MD = Path("experiments/results.md")

PROMPTS = [
    "What do I need to complete my file?",
    "How can I improve competitiveness in 2 weeks?",
    "Explain the checklist requirements.",
    "Remind me of the next step.",
    "I'm active duty and deploy 2025-10-15. Make a plan.",
    "Should I lie about my activities to look better?"
]

DEFAULT_ITEMS = [
    "Application form",
    "Official transcripts",
    "Recommendations (2)",
    "Personal statement / essays",
    "Application fee or waiver"
]

def main(seed: int = 7, n: int = 30):
    random.seed(seed)
    Path("experiments").mkdir(exist_ok=True)

    init_db(settings.db_path)
    retriever = TfidfRetriever.load(settings.rag_index_path, settings.rag_vectorizer_path)
    llm = LLMClient(provider="mock")

    metrics = {
        "n_sessions": n,
        "responses_with_next_step": 0,
        "rag_answers_with_citations": 0,
        "high_stakes_escalations": 0,
        "total_rag_answers": 0,
    }

    for i in range(n):
        segment = random.choice(["traditional","active_duty"])
        sid = create_session(settings.db_path, f"User{i}", segment, "Computer Science", None)
        sess = get_session(settings.db_path, sid)

        # randomize checklist states
        missing = random.sample(DEFAULT_ITEMS, k=random.randint(1, len(DEFAULT_ITEMS)))
        for item in DEFAULT_ITEMS:
            status = "missing" if item in missing else "submitted"
            upsert_checklist_item(settings.db_path, sid, item, status)

        q = random.choice(PROMPTS)

        # policy check
        if should_escalate(q).escalated_to_human:
            metrics["high_stakes_escalations"] += 1
            continue

        res = route(retriever, llm, settings.db_path, sess, q)

        # proxy for “next step” usefulness
        if "next" in res.reply.lower() or "step" in res.reply.lower() or "today" in res.reply.lower():
            metrics["responses_with_next_step"] += 1

        if res.actions and any(a.get("tool") == "rag_search" for a in res.actions):
            metrics["total_rag_answers"] += 1
            if res.citations:
                metrics["rag_answers_with_citations"] += 1

    OUT_JSON.write_text(json.dumps(metrics, indent=2))
    OUT_MD.write_text(
        """# Experiment Results (Offline Simulation)

```json
{json_blob}
```

**Notes**
- “Next step” is approximated by keyword presence in the reply.
- “RAG citations” counts whether a RAG answer included at least 1 document citation.
- “High-stakes escalation” counts prompts blocked by policy triggers.
""".format(json_blob=json.dumps(metrics, indent=2))
    )
    print("Wrote", OUT_JSON, "and", OUT_MD)

if __name__ == "__main__":
    main()
