#!/bin/sh

set -e

gunicorn -b 0.0.0.0:$PORT -k uvicorn.workers.UvicornWorker app.main:app

celery worker -A app.background.worker -l INFO