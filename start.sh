#!/bin/bash
pip install -r requirements-updated.txt
python init_db.py
uvicorn app:app --host 0.0.0.0 --port 10000
