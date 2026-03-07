FROM python:3.13-alpine

WORKDIR /app

COPY sync_new_posts.py .

CMD ["python", "sync_new_posts.py"]
