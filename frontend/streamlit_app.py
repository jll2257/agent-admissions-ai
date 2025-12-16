import streamlit as st
import requests
from datetime import date

API = st.secrets.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Agentic Admissions Concierge (AAC)", layout="wide")

st.title("Agentic Admissions Concierge (AAC) — Demo")
st.caption("Columbia-only demo: answers are grounded in official Columbia Undergraduate Admissions pages.")

with st.sidebar:
    st.header("Create / Load Session")

    # Demo applicants (loaded from the backend dataset)
    applicants = []
    try:
        applicants = requests.get(f"{API}/applicants", timeout=10).json()
    except Exception:
        applicants = []

    applicant_options = {"Custom (type manually)": None}
    for a in applicants:
        label = f"{a['applicant_number']} — {a['name']['last']}, {a['name']['first']} (SAT {a['sat']}, GPA {a['gpa']})"
        applicant_options[label] = a["applicant_number"]

    chosen_label = st.selectbox("Demo applicant", list(applicant_options.keys()))
    chosen_applicant_number = applicant_options[chosen_label]

    if chosen_applicant_number:
        chosen = next(x for x in applicants if x["applicant_number"] == chosen_applicant_number)
        name = f"{chosen['name']['last']}, {chosen['name']['first']}"
        segment = "traditional"
        program = "Columbia Undergraduate Admissions"
        deadline = None
    else:
        name = st.text_input("Applicant name", "Alex")
        segment = st.selectbox("Applicant segment", ["traditional","transfer","international","active_duty"])
        program = st.text_input("Target program", "Columbia Undergraduate Admissions")
        deadline = st.date_input("Target deadline (optional)", value=None)

    if st.button("Create session"):
        payload = {
            "name": name,
            "segment": segment,
            "target_program": program,
            "deadline": str(deadline) if deadline else None,
            "applicant_number": chosen_applicant_number,
        }
        r = requests.post(f"{API}/sessions", json=payload, timeout=15)
        r.raise_for_status()
        st.session_state["session"] = r.json()

    sid = st.text_input("Or load session_id")
    if st.button("Load session"):
        r = requests.get(f"{API}/sessions/{sid}", timeout=15)
        r.raise_for_status()
        st.session_state["session"] = r.json()

    st.divider()
    st.subheader("Columbia official pages used")
    st.markdown("- [Apply](https://undergrad.admissions.columbia.edu/apply)")
    st.markdown("- [Application Process](https://undergrad.admissions.columbia.edu/apply/process)")
    st.markdown("- [FAQ](https://undergrad.admissions.columbia.edu/faq)")
    st.markdown("- [Resources](https://undergrad.admissions.columbia.edu/resources)")
    st.markdown("- [Academics](https://undergrad.admissions.columbia.edu/academics)")

    st.divider()
    st.subheader("Suggested demo prompts")
    st.write("- What items are required to complete my Columbia application file?")
    st.write("- Based on my file completion, what should I do next to reach 100%?")
    st.write("- What does Columbia say about the application process and required materials?")

sess = st.session_state.get("session")
if not sess:
    st.info("Create or load a session from the sidebar.")
    st.stop()

st.success(f"Session loaded: {sess['session_id']}  |  Segment: {sess['segment']}  |  Program: {sess['target_program']}")

if "chat" not in st.session_state:
    st.session_state["chat"] = []

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Chat")
    for msg in st.session_state["chat"]:
        role = msg["role"]
        if role == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
            if msg.get("citations"):
                with st.expander("Citations"):
                    for c in msg["citations"]:
                        st.write(f"**{c['doc_id']}** — {c['title']}")
                        st.write(c["snippet"])

    user_msg = st.chat_input("Ask the admissions concierge…")
    if user_msg:
        st.session_state["chat"].append({"role":"user","content":user_msg})
        r = requests.post(f"{API}/chat", json={"session_id": sess["session_id"], "message": user_msg}, timeout=30)
        r.raise_for_status()
        out = r.json()
        st.session_state["chat"].append({
            "role":"assistant",
            "content": out["reply"],
            "citations": out.get("citations", []),
            "actions": out.get("actions", []),
            "escalated": out.get("escalated_to_human", False),
        })
        st.rerun()

with col2:
    st.subheader("Applicant Snapshot")
    try:
        prof = requests.get(f"{API}/sessions/{sess['session_id']}/profile", timeout=10).json()
        st.write(f"**Applicant:** {prof.get('last_name')}, {prof.get('first_name')}  |  **#{prof.get('applicant_number')}**")
        st.write(f"**SAT:** {prof.get('sat')}  |  **GPA:** {prof.get('gpa')}")
        st.write(f"**File completion:** {prof.get('file_completion_pct')}%  |  **Estimated chance (demo):** {prof.get('estimated_chance_pct')}%")
        extra = prof.get('extracurriculars') or ''
        if extra:
            st.write("**Extracurriculars:** " + extra)
    except Exception:
        st.caption("No mock profile attached to this session (custom session).")

    st.subheader("Agent Trace (Tools / Actions)")
    if st.session_state["chat"]:
        last = next((m for m in reversed(st.session_state["chat"]) if m["role"] == "assistant"), None)
        if last:
            st.json(last.get("actions", []))
            if last.get("escalated"):
                st.warning("Escalated to a human due to policy triggers.")
    st.subheader("What this demo shows")
    st.markdown("""
    - **RAG**: answers can cite local policy/FAQ docs  
    - **Tool use**: checklist + deployment buffer + nudges  
    - **Multi-agent routing**: different specialists handle different intents  
    - **Human-in-the-loop**: escalation for high-stakes/integrity topics  
    """)
