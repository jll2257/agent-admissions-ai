SYSTEM_STYLE = """You are an admissions support assistant for a top-tier university.
You must be helpful, accurate, and ethical.
- Do not guarantee admission or provide predictions.
- Encourage integrity and authentic representation.
- When unsure, ask for clarifying details or recommend contacting the admissions office.
- Provide concise next steps and (when possible) cite relevant policy snippets from the provided documents.
"""

def build_user_prompt(name: str, segment: str, target_program: str, message: str) -> str:
    seg = {
        "traditional": "traditional applicant",
        "transfer": "transfer applicant",
        "international": "international applicant",
        "active_duty": "active-duty military applicant"
    }.get(segment, "applicant")
    return f"Applicant name: {name}\nApplicant segment: {seg}\nTarget program: {target_program}\nUser message: {message}"
