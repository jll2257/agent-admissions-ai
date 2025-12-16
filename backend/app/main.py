from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import SessionCreate, Session, ChatRequest, ChatResponse, Citation
from .db import (
    init_db,
    create_session,
    get_session,
    add_message,
    upsert_checklist_item,
    get_checklist,
    upsert_applicant_profile,
    get_applicant_profile,
)
from .applicants import (
    load_applicants,
    get_applicant,
    applicant_as_dict,
    applicant_checklist,
    CHECKLIST_ITEMS,
    compute_file_completion,
)
from .rag.retriever import TfidfRetriever
from .llm import LLMClient
from .agents.router import route
from .policies import should_escalate

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-loaded resources
retriever: TfidfRetriever | None = None
llm = LLMClient(provider="mock")
applicants_cache = []

@app.on_event("startup")
def _startup():
    init_db(settings.db_path)
    # Load demo applicants (optional). If missing, the demo can still run.
    global applicants_cache
    applicants_cache = load_applicants(settings.applicants_path)


def _make_completion_nudge(session_id: str) -> str:
    """Append a deterministic, user-facing nudge to complete the application file."""
    cl = get_checklist(settings.db_path, session_id)
    status_by_item = {c["item"]: c["status"] for c in cl}
    pct = compute_file_completion(status_by_item)
    missing = [i for i in CHECKLIST_ITEMS if status_by_item.get(i) != "complete"]

    # Keep profile up to date if it exists
    prof = get_applicant_profile(settings.db_path, session_id) or {}
    if prof:
        prof["file_completion_pct"] = pct
        upsert_applicant_profile(settings.db_path, session_id, {
            "applicant_number": prof.get("applicant_number"),
            "name": {"last": prof.get("last_name"), "first": prof.get("first_name")},
            "sat": prof.get("sat"),
            "gpa": prof.get("gpa"),
            "extracurriculars": (prof.get("extracurriculars") or "").split("; ") if prof.get("extracurriculars") else [],
            "estimated_admission_chance_pct": prof.get("estimated_chance_pct"),
            "file_completion_pct": pct,
        })

    chance = prof.get("estimated_chance_pct")
    header = f"\n\n---\n**File completion:** {pct}%"
    if chance is not None:
        header += f"  |  **Estimated admission chance (demo heuristic):** {int(chance)}%"
    header += "\n"

    if not missing:
        return header + "✅ Your core file items are marked complete. Next: confirm submission + review Columbia-specific requirements." 

    lines = [header, "**Recommended next steps (to reach 100%):**"]
    for i, item in enumerate(missing[:3], start=1):
        lines.append(f"{i}. Finish: **{item}**")
    if len(missing) > 3:
        lines.append(f"(+{len(missing)-3} more items remaining)")
    lines.append("\nOfficial Columbia admissions pages used for this demo:")
    for url in settings.columbia_sources:
        lines.append(f"- {url}")
    return "\n".join(lines)

def _get_retriever() -> TfidfRetriever:
    global retriever
    if retriever is None:
        try:
            retriever = TfidfRetriever.load(settings.rag_index_path, settings.rag_vectorizer_path)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="RAG index not found. Run: python -m scripts.build_index")
    return retriever

@app.post("/sessions", response_model=Session)
def create_session_api(req: SessionCreate):
    # If an applicant_number is provided, bootstrap the session from the mock dataset.
    name = req.name
    if req.applicant_number:
        app_rec = get_applicant(applicants_cache, req.applicant_number)
        if not app_rec:
            raise HTTPException(status_code=404, detail="Applicant not found in demo dataset")
        profile = applicant_as_dict(app_rec)
        name = f"{app_rec.last_name}, {app_rec.first_name}"

    sid = create_session(
        settings.db_path,
        name=name,
        segment=req.segment,
        target_program=req.target_program,
        deadline=req.deadline.isoformat() if req.deadline else None,
    )

    # Bootstrap checklist + profile if using the dataset
    if req.applicant_number:
        for item, status in applicant_checklist(app_rec).items():
            upsert_checklist_item(settings.db_path, sid, item, status)
        upsert_applicant_profile(settings.db_path, sid, profile)
    s = get_session(settings.db_path, sid)
    return Session(**s)

@app.get("/sessions/{session_id}", response_model=Session)
def get_session_api(session_id: str):
    s = get_session(settings.db_path, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return Session(**s)


@app.get("/applicants")
def list_applicants_api():
    """Return the mock applicant dataset used for the demo."""
    return [applicant_as_dict(a) for a in applicants_cache]


@app.get("/applicants/{applicant_number}")
def get_applicant_api(applicant_number: str):
    a = get_applicant(applicants_cache, applicant_number)
    if not a:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant_as_dict(a)


@app.get("/sessions/{session_id}/profile")
def get_profile_api(session_id: str):
    p = get_applicant_profile(settings.db_path, session_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found for this session")
    return p

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    s = get_session(settings.db_path, req.session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    add_message(settings.db_path, req.session_id, "user", req.message)

    # policy screening
    decision = should_escalate(req.message)
    if decision.escalated_to_human:
        reply = ("This question may involve high-stakes policy or integrity issues. "
                 "I recommend contacting the admissions office or a counselor for guidance. "
                 f"(Reason: {decision.reason})")
        add_message(settings.db_path, req.session_id, "assistant", reply)
        return ChatResponse(session_id=req.session_id, reply=reply, actions=[{"tool":"escalate","reason":decision.reason}],
                            citations=[], escalated_to_human=True)

    r = _get_retriever()
    result = route(r, llm, settings.db_path, s, req.message)

    # Always append a completion nudge so the demo "pushes" applicants toward file completion.
    final_reply = result.reply + _make_completion_nudge(req.session_id)

    add_message(settings.db_path, req.session_id, "assistant", final_reply)
    return ChatResponse(
        session_id=req.session_id,
        reply=final_reply,
        actions=result.actions,
        citations=[Citation(**c) for c in result.citations],
        escalated_to_human=result.escalated_to_human,
    )
