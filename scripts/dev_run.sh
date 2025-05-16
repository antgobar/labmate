#!/bin/bash
source .venv/bin/activate;
uvicorn app.main:app --port 8000 --reload