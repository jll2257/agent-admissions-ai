from __future__ import annotations
from typing import Dict, Any, List

from .base import AgentResult
from ..rag.retriever import TfidfRetriever
from ..config import settings
from ..llm import LLMClient
from ..policies import enforce_no_guarantees

def run(retriever: TfidfRetriever, llm: LLMClient, session: Dict[str, Any], message: str) -> AgentResult:
    hits = retriever.search(message, top_k=settings.top_k_docs)
    citations = []
    context_chunks = []
    for doc, score in hits:
        snippet = TfidfRetriever.make_snippet(doc.text, 280)
        citations.append({"doc_id": doc.doc_id, "title": doc.title, "snippet": snippet})
        context_chunks.append(f"[{doc.doc_id}] {doc.title}\n{snippet}")
    context = "\n\n".join(context_chunks) if context_chunks else ""
    draft = llm.generate(system="Admissions support", user=message, context=context)
    reply = draft
    if context:
        reply += "\n\nSources:\n" + "\n".join([f"- {c['doc_id']}: {c['title']}" for c in citations])
    reply = enforce_no_guarantees(reply)
    return AgentResult(reply=reply, actions=[{"tool":"rag_search","hits":len(hits)}], citations=citations)
