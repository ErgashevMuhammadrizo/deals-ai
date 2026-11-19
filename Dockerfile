FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/deals-ai
RUN useradd -m -u 10001 app && mkdir -p /srv/deals-ai/backend/media /srv/deals-ai/backend/staticfiles && chown -R app:app /srv/deals-ai
COPY backend/requirements.txt /srv/deals-ai/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY --chown=app:app backend /srv/deals-ai/backend
COPY --chown=app:app frontend /srv/deals-ai/frontend
COPY --chown=app:app scripts /srv/deals-ai/scripts
USER app
WORKDIR /srv/deals-ai/backend
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","2","--timeout","90"]
