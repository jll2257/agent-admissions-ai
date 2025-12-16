import sqlite3
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str) -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
      session_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      segment TEXT NOT NULL,
      target_program TEXT NOT NULL,
      deadline TEXT NULL,
      created_at TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS checklist (
      session_id TEXT NOT NULL,
      item TEXT NOT NULL,
      status TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      PRIMARY KEY (session_id, item)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    """)

    # Optional profile info for demo applicants (stored per session)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applicant_profiles (
      session_id TEXT PRIMARY KEY,
      applicant_number TEXT NULL,
      last_name TEXT NULL,
      first_name TEXT NULL,
      sat INTEGER NULL,
      gpa REAL NULL,
      extracurriculars TEXT NULL,
      estimated_chance_pct INTEGER NULL,
      file_completion_pct INTEGER NULL,
      updated_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def create_session(db_path: str, name: str, segment: str, target_program: str, deadline: Optional[str]) -> str:
    sid = str(uuid.uuid4())
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions(session_id,name,segment,target_program,deadline,created_at) VALUES (?,?,?,?,?,?)",
        (sid, name, segment, target_program, deadline, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    return sid

def get_session(db_path: str, session_id: str) -> Optional[Dict[str, Any]]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def upsert_checklist_item(db_path: str, session_id: str, item: str, status: str) -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO checklist(session_id,item,status,updated_at)
             VALUES (?,?,?,?)
             ON CONFLICT(session_id,item) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at""",
        (session_id, item, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_checklist(db_path: str, session_id: str) -> List[Dict[str, Any]]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT item,status,updated_at FROM checklist WHERE session_id=? ORDER BY item", (session_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_message(db_path: str, session_id: str, role: str, content: str) -> None:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages(session_id,role,content,created_at) VALUES (?,?,?,?)",
        (session_id, role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_messages(db_path: str, session_id: str, limit: int = 12) -> List[Dict[str, Any]]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT role,content,created_at FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))


def upsert_applicant_profile(db_path: str, session_id: str, profile: Dict[str, Any]) -> None:
    """Upsert demo applicant profile fields for a session."""
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO applicant_profiles(
               session_id, applicant_number, last_name, first_name, sat, gpa,
               extracurriculars, estimated_chance_pct, file_completion_pct, updated_at
             ) VALUES (?,?,?,?,?,?,?,?,?,?)
             ON CONFLICT(session_id) DO UPDATE SET
               applicant_number=excluded.applicant_number,
               last_name=excluded.last_name,
               first_name=excluded.first_name,
               sat=excluded.sat,
               gpa=excluded.gpa,
               extracurriculars=excluded.extracurriculars,
               estimated_chance_pct=excluded.estimated_chance_pct,
               file_completion_pct=excluded.file_completion_pct,
               updated_at=excluded.updated_at""",
        (
            session_id,
            profile.get("applicant_number"),
            (profile.get("name") or {}).get("last"),
            (profile.get("name") or {}).get("first"),
            profile.get("sat"),
            profile.get("gpa"),
            "; ".join(profile.get("extracurriculars") or []),
            profile.get("estimated_admission_chance_pct"),
            profile.get("file_completion_pct"),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_applicant_profile(db_path: str, session_id: str) -> Optional[Dict[str, Any]]:
    conn = _connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicant_profiles WHERE session_id=?", (session_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
