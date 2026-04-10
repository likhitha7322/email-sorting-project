FROM python:3.10-slim

LABEL maintainer="OpenEnv Hackathon Team"
LABEL description="Email Sorting OpenEnv — AI email classification environment"
LABEL version="1.0.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "inference.py"]
