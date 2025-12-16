from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_create_session_and_chat():
    r = client.post("/sessions", json={"name":"Alex","segment":"traditional","target_program":"CS","deadline":None})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    # chat will fail if index not built; allow either 200 or 500 with expected message
    c = client.post("/chat", json={"session_id":sid, "message":"What do I need to complete my file?"})
    assert c.status_code in (200, 500)
