# Agentic Admissions Concierge (AAC) — Demo Project

**Goal:** A human-centered, agentic AI demo for *top-tier university admissions* that:
1) attracts and activates applicants,  
2) speeds “start → file complete”, and  
3) motivates applicants to strengthen competitiveness during the process,
with **special support for active-duty military applicants**.

This repo is structured to satisfy typical course project requirements for:
- code quality (clean structure, docs, tests, error handling),
- functionality (working demo + integration tests),
- experiment results (reproducible eval script + results),
- step-by-step tutorial (install, run, usage examples, troubleshooting).

---

## 1) Quickstart (local demo — no API keys required)

**Demo scope (latest update):** Columbia Undergraduate Admissions only. The RAG index is built from
five official Columbia pages (Apply, Process, FAQ, Resources, Academics) and the UI includes a
5-applicant mock dataset for an interactive demo.

### Prereqs
- Python 3.10+

### Setup
```bash
cd admissions_agentic_ai_demo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Fetch Columbia sources + build the local knowledge base index (RAG)
```bash
python -m scripts.fetch_columbia_docs
python -m scripts.build_index
```

### Run the API (FastAPI)
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

### Run the UI (Streamlit)
```bash
streamlit run frontend/streamlit_app.py
```

---

## 2) What’s implemented (features)

### Applicant funnel support (retain + accelerate)
- **Outreach nudges**: personalized “next best step” guidance
- **Checklist tracker**: file completion status, missing items, reminders
- **Competitiveness coach**: suggests improvements *without* guaranteeing admission
- **RAG-backed Q&A**: answers with citations to local policy/FAQ docs

### Special audience: Active-duty military
- **deployment-aware timeline** and alternative steps
- **experience translation**: military → leadership/impact framing
- **handoff to humans** when high-stakes or policy-sensitive

### Human agency + guardrails
- The agent **never makes admissions decisions**.
- High-stakes outputs (e.g., “should I disclose X?”) trigger a **human escalation**.
- A “policy layer” enforces safe messaging and avoids promises.

---

## 3) Architecture (mapped to course topics)

- **LLM app + prompt engineering:** `backend/app/agents/*`, `backend/app/prompts.py`
- **RAG:** `backend/app/rag/*` (TF-IDF retriever for offline reproducibility)
- **Tool-assisted agents:** `backend/app/tools.py` (retrieve, checklist update, schedule, nudge)
- **Multi-agent:** specialist agents + router in `backend/app/agents/router.py`
- **Memory / “MCP-like” sessions:** per-applicant state in SQLite `backend/app/db.py`

> Optional upgrade paths (not required for demo):
> - swap TF-IDF for embeddings (e.g., sentence-transformers + FAISS),
> - connect to CRM/LMS sandbox,
> - add real LLM provider (OpenAI/Anthropic/local vLLM) via `LLMClient`.

---

## 4) Usage examples

### Create an applicant session (custom)
```bash
curl -X POST http://127.0.0.1:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name":"Alex","segment":"active_duty","target_program":"Computer Science","deadline":"2025-12-01"}'
```

### Create a session from the mock dataset
```bash
curl -X POST http://127.0.0.1:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"name":"(ignored)","segment":"traditional","target_program":"Columbia Undergraduate Admissions","applicant_number":"2029002"}'
```

### Ask a question (RAG)
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<SESSION_ID>","message":"What do I need to complete my file?"}'
```

---

## 5) Reproducible experiments / evaluation

Run:
```bash
python scripts/eval_simulation.py
```
Outputs:
- `experiments/results.json`
- `experiments/results.md`

The evaluation uses a small **synthetic applicant simulator** to measure:
- time-to-first-action
- checklist completion rate
- escalation rate
- hallucination risk proxy (answers without citations)

---

## 6) Tests

```bash
pytest -q
```

---

## 7) Troubleshooting

**Issue:** `ModuleNotFoundError`  
**Fix:** ensure you installed requirements and are running from repo root.

**Issue:** empty search results  
**Fix:** run `python -m scripts.fetch_columbia_docs` then `python -m scripts.build_index`; confirm `data/columbia_docs/*.md` exist.

**Issue:** port in use  
**Fix:** change API port: `uvicorn ... --port 8010`

---

## License
Educational demo.
