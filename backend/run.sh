#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m pip install -r requirements.txt
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
