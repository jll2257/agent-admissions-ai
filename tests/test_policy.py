from backend.app.policies import should_escalate

def test_escalate_integrity():
    d = should_escalate("Should I lie on my application?")
    assert d.escalated_to_human is True

def test_no_escalate_normal():
    d = should_escalate("What is a recommendation letter?")
    assert d.escalated_to_human is False
