FROM python:3.12
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN chmod +x dev_run.sh 
RUN chmod +x prod_run.sh
EXPOSE 8000
ENTRYPOINT ["./dev_run.sh"]