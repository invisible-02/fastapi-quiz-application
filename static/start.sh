#!/bin/bash
# Install dependencies
pip install -r requirements-updated.txt

# Initialize the database
python init_db.py

# Start the application
uvicorn app:app --host 0.0.0.0 --port 8000
