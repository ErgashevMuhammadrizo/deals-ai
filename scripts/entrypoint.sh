#!/bin/sh
set -eu
cd /srv/deals-ai/backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
