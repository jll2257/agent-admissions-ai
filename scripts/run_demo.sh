#!/usr/bin/env bash
set -euo pipefail

python -m scripts.fetch_columbia_docs
python -m scripts.build_index
python -m uvicorn backend.app.main:app --port 8000 --reload &
API_PID=$!
sleep 1
streamlit run frontend/streamlit_app.py

kill $API_PID || true
