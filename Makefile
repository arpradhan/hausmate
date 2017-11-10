PROJECT_NAME := hausmate

.DEFAULT_GOAL := help

help:
	@echo "help 							Print this help."
	@echo "build							Build Docker image."
	@echo "push								Push Docker image to GCR."
	@echo "up									Start services."
	@echo "stop								Stop services."
	@echo "rm									Remove services."
	@echo "static							Collect static files for django app."
	@echo "bash								Start bash session on web container."


build:
	@docker build -t hausmate ./hausmate

push:
	@docker tag hausmate gcr.io/hausmate-185516/hausmate
	@gcloud docker -- push gcr.io/hausmate-185516/hausmate

up:
	@docker-compose up

stop:
	@docker-compose stop

rm:
	@docker-comopose rm -f

static:
	@docker-compose exec web ./manage.py collectstatic --noinput

bash:
	@docker-compose exec web bash
