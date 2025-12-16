from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any


CHECKLIST_ITEMS = [
    "SAT score",
    "Official transcripts",
    "Essays",
    "Letters of recommendation",
]


@dataclass
class Applicant:
    applicant_number: str
    last_name: str
    first_name: str
    sat: int
    gpa: float
    transcripts: str
    essay: str
    lor: str
    extracurriculars: List[str]

    @property
    def full_name(self) -> str:
        return f"{self.last_name}, {self.first_name}"


def compute_admission_chance(sat: int, gpa: float) -> int:
    """Rule-based estimate for demo only.

    Baseline: 80% if sat>=1400 and gpa>=3.5
    Add +5% for each full +100 SAT above 1400
    Add +5% for each full +0.1 GPA above 3.5
    Cap at 99%.
    """
    base = 80 if (sat >= 1400 and gpa >= 3.5) else 70
    sat_bonus = max(0, (sat - 1400) // 100) * 5
    gpa_bonus = max(0, int((gpa - 3.5) // 0.1)) * 5
    chance = base + sat_bonus + gpa_bonus
    return int(min(99, max(0, chance)))


def compute_file_completion(checklist_status: Dict[str, str]) -> int:
    """Compute % complete for the 4 checklist items.

    Any item with status == 'complete' counts. Others do not.
    """
    completed = sum(1 for k in CHECKLIST_ITEMS if checklist_status.get(k) == "complete")
    return int(round((completed / len(CHECKLIST_ITEMS)) * 100))


def load_applicants(csv_path: str) -> List[Applicant]:
    path = Path(csv_path)
    if not path.exists():
        return []
    out: List[Applicant] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            extracurriculars = [x.strip() for x in (r.get("extracurriculars") or "").split(";") if x.strip()]
            out.append(
                Applicant(
                    applicant_number=str(r["applicant_number"]),
                    last_name=r["last_name"],
                    first_name=r["first_name"],
                    sat=int(r["sat"]),
                    gpa=float(r["gpa"]),
                    transcripts=r["transcripts"],
                    essay=r["essay"],
                    lor=r["lor"],
                    extracurriculars=extracurriculars,
                )
            )
    return out


def applicant_checklist(app: Applicant) -> Dict[str, str]:
    # SAT is treated as complete if score is present
    return {
        "SAT score": "complete" if app.sat else "missing",
        "Official transcripts": app.transcripts,
        "Essays": app.essay,
        "Letters of recommendation": app.lor,
    }


def applicant_as_dict(app: Applicant) -> Dict[str, Any]:
    cl = applicant_checklist(app)
    return {
        "applicant_number": app.applicant_number,
        "name": {"last": app.last_name, "first": app.first_name},
        "sat": app.sat,
        "gpa": app.gpa,
        "extracurriculars": app.extracurriculars,
        "checklist": cl,
        "file_completion_pct": compute_file_completion(cl),
        "estimated_admission_chance_pct": compute_admission_chance(app.sat, app.gpa),
    }


def get_applicant(applicants: List[Applicant], applicant_number: str) -> Optional[Applicant]:
    for a in applicants:
        if a.applicant_number == str(applicant_number):
            return a
    return None
