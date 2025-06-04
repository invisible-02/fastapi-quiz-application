#!/bin/bash
python init_db.py
uvicorn app:app --host 0.0.0.0 --port 3000
