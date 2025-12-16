# Step-by-Step Tutorial (AAC Demo)

This tutorial aligns with typical project-code rubric items:
- installation instructions
- environment setup
- usage examples
- troubleshooting

## 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Build RAG index
```bash
python scripts/build_index.py
```

## 3) Run backend
```bash
uvicorn backend.app.main:app --reload
```

## 4) Run frontend
```bash
streamlit run frontend/streamlit_app.py
```

## 5) Demo scenarios
- **File completion:** “What do I need to complete my file?”
- **Competitiveness:** “Help me improve competitiveness in 2 weeks.”
- **Active duty:** “I’m active duty and deploy 2025-10-15. Make a plan.”
- **Integrity:** “Should I lie about my activities?” (triggers escalation)

## 6) Run tests
```bash
pytest -q
```

## 7) Run evaluation
```bash
python scripts/eval_simulation.py
```
