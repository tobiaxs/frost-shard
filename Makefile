.PHONY: lint
## Run pre-commit checks
lint:
	poetry run pre-commit run --all-files

.PHONY: test
## Run tests with pytest
test:
	poetry run pytest

.PHONY: makemigrations
## Generate migrations with alembic
makemigrations:
	poetry run alembic revision --autogenerate

.PHONY: migrate
## Run migrations with alembic
migrate:
	poetry run alembic upgrade head
