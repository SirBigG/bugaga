set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

repo_dir := justfile_directory()
python := repo_dir + "/.venv/bin/python"
pytest := repo_dir + "/.venv/bin/pytest"
ruff := repo_dir + "/.venv/bin/ruff"
compose := "docker compose --project-directory " + repo_dir + " -f " + repo_dir + "/docker-compose.yml"
django_compose := compose + " -f " + repo_dir + "/docker-compose.django.yml --profile modernization"
django_image := "bugaga-django:test"
docker_hub_repository := "sirbigg/bugaga"
docker_platform := "linux/x86_64"

# Show available commands.
default:
    @just --list

# Install the locked development environment.
setup:
    uv sync --frozen --group dev

# Update uv.lock after an intentional dependency change.
lock:
    uv lock

# Format Python code and apply safe lint fixes.
format:
    {{ ruff }} check --fix src manage.py
    {{ ruff }} format src manage.py

# Run lint, Django system checks, and migration drift checks.
check:
    {{ ruff }} check src manage.py
    {{ python }} manage.py check --settings=config.settings.test
    {{ python }} manage.py makemigrations --check --dry-run --settings=config.settings.test

# Run the new Django test suite.
test:
    {{ pytest }} -q

# Run all local Django verification.
verify: check test

# Run an arbitrary Django management command with development settings.
manage *args:
    {{ python }} manage.py {{ args }}

# Run Django migrations locally.
migrate *args:
    {{ python }} manage.py migrate {{ args }} --settings=config.settings.development

# Create Django migrations locally.
makemigrations *args:
    {{ python }} manage.py makemigrations {{ args }} --settings=config.settings.development

# Open a local Django shell.
shell:
    {{ python }} manage.py shell --settings=config.settings.development

# Start the local Django development server outside Docker.
dev:
    {{ python }} manage.py runserver 0.0.0.0:8000 --settings=config.settings.development

# Validate the merged legacy and Django Compose configuration.
compose-check:
    {{ django_compose }} config --quiet

# Start the Django service beside the legacy service on 127.0.0.1:8282.
up:
    {{ django_compose }} up --build django

# Start the Django service in the background.
start:
    {{ django_compose }} up -d --build django

# Stop the parallel Django service and its database dependency.
stop:
    {{ django_compose }} stop django db

# Show service status.
ps:
    {{ django_compose }} ps

# Follow Django service logs.
logs:
    {{ django_compose }} logs -f django

# Build the Django production image.
build:
    docker build -f Dockerfile.django -t {{ django_image }} .

# Build and publish the Django image for the production server.
publish tag:
    docker build --platform {{ docker_platform }} -f Dockerfile.django -t "{{ docker_hub_repository }}:{{ tag }}" .
    docker push "{{ docker_hub_repository }}:{{ tag }}"

# Pull a published Django image on the production server.
pull:
    {{ django_compose }} pull django

# Start the already-pulled Django image without building on the server.
deploy:
    {{ django_compose }} up -d --no-build django

# Run the legacy unittest suite in its existing container image.
legacy-test:
    {{ compose }} run --rm admin python -m unittest discover . "test_*.py"

# Export the current PostgreSQL schema without table data.
schema-dump output="bugaga-schema.sql":
    {{ compose }} exec -T db sh -c 'pg_dump --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --schema-only --no-owner --no-privileges' > "{{ output }}"

# Create a private custom-format PostgreSQL backup before cutover.
backup output="bugaga-production.dump":
    {{ compose }} exec -T db sh -c 'pg_dump --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --format=custom --no-owner --no-privileges' > "{{ output }}"
