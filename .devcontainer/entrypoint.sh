#!/bin/sh
set -e

cd /workspace
alembic upgrade heads

# cd /workspace/frontend
# npm start > /proc/1/fd/1 2<&1 < /proc/1/fd/1 &

cd /workspace
celery -A crawl_tweet_tasks.celery_app worker --concurrency=2 --prefetch-multiplier=20 --pool=threads --loglevel=info > /proc/1/fd/1 2<&1 < /proc/1/fd/1 &
python3 -m uvicorn main:app --host=0.0.0.0
