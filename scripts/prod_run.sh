#!/bin/bash
alembic upgrade head;
fastapi run app/main.py