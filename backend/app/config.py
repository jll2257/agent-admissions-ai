from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Agentic Admissions Concierge (AAC)"
    db_path: str = "backend/app/aac.db"
    rag_index_path: str = "backend/app/rag/index.pkl"
    rag_vectorizer_path: str = "backend/app/rag/vectorizer.pkl"
    top_k_docs: int = 4

    # Demo data
    applicants_path: str = "data/applicants_columbia.csv"

    # Columbia Undergraduate Admissions (demo scope)
    columbia_sources: list[str] = [
        "https://undergrad.admissions.columbia.edu/apply/process",
        "https://undergrad.admissions.columbia.edu/resources",
        "https://undergrad.admissions.columbia.edu/faq",
        "https://undergrad.admissions.columbia.edu/apply",
        "https://undergrad.admissions.columbia.edu/academics",
    ]

settings = Settings()
