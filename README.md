# Project Setup Guide

## Backend Setup

1. Navigate to the `.devcontainer` folder:
   ```bash
   cd .devcontainer
   ```

2. Start the Docker containers:
   ```bash
   docker compose up -d
   ```

3. After Docker is set up, run the Alembic migrations:
   ```bash
   alembic upgrade heads
   ```

4. Start the Celery worker:
   ```bash
   celery -A crawl_tweet_tasks.celery_app worker --concurrency=2 --prefetch-multiplier=20 --pool=threads --loglevel=info
   ```

5. Launch the Uvicorn server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0
   ```

## Frontend Setup

1. Start the Docker containers:
   ```bash
   docker compose up -d
   ```

