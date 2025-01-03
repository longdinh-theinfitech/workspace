from celery import Celery

# CELERY_BROKER_URL = "redis://:twitter@redis-stack:6379/0"
# CELERY_BROKER_URL = "sqla+postgresql://postgres:postgres@base-db:5432/postgres"
# CELERY_RESULT_BACKEND = "db+postgresql://postgres:postgres@base-db:5432/postgres"

queue_name = "crawl_tweet_tasks"
celery_crawler = Celery(
    queue_name,
    broker="sqla+postgresql://postgres:postgres@base-db:5432/lookback",
    result_backend='db+postgresql://postgres:postgres@base-db:5432/lookback',
    # task_always_eager=True,
)
