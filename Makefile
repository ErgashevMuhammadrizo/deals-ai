.PHONY: up down logs shell check test superuser
up:
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f web
shell:
	docker compose exec web python manage.py shell
check:
	docker compose exec web python manage.py check
superuser:
	docker compose exec web python manage.py createsuperuser
test:
	docker compose exec web python manage.py test apps.core
