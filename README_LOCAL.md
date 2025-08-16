# SocialMediaRAG — Minimal Backend (Windows Local Setup)

This zip contains a complete FastAPI backend that boots cleanly.

## Setup (Windows CMD)
```
cd path\to\SocialMediaRAG_SingleService\backend
py -3.10 -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visit: http://127.0.0.1:8000/api/health
