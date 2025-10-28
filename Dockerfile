FROM python:3.11-slim
WORKDIR /formDB
COPY requirements.txt
RUN pip install flask flask-wtf wtforms
RUN pip install --no-cache-dir -r requirements.txt
