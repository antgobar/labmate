FROM python:3.12-slim as builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN addgroup --system appgroup && \
    adduser --system --no-create-home --ingroup appgroup appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY --chown=appuser:appgroup . .
RUN chown -R appuser:appgroup /opt/venv
USER appuser
EXPOSE 8000
ENTRYPOINT ["sh", "-c", "fastapi run app/main.py"]