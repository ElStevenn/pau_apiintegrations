.PHONY: up down rebuild logs exec

ENV_FILE_PATH=$(shell realpath src/secrets/.env)

up:
	@docker-compose --env-file $(ENV_FILE_PATH) up -d --build
	@echo "Application is running on http://localhost"

down:
	@docker-compose --env-file $(ENV_FILE_PATH) down --rmi all --volumes --remove-orphans

rebuild:
	@make down
	@docker-compose --env-file $(ENV_FILE_PATH) build
	@make up

logs:
	@docker-compose --env-file $(ENV_FILE_PATH) logs -f
	@echo "Logs are being displayed. Press Ctrl+C to stop."

exec:
	@docker-compose --env-file $(ENV_FILE_PATH) run --rm --entrypoint bash integration_application
	@echo "You are now inside a one‑off container. Press Ctrl+D to exit."
