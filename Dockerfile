FROM python:3.12
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
EXPOSE 8000
RUN alembic upgrade head
ENTRYPOINT ["sh", "-c", "alembic upgrade head && fastapi run app/main.py"]