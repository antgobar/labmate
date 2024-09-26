#!/bin/bash
# alembic upgrade head;
uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=.ssl/server.key --ssl-certfile=.ssl/server.crt