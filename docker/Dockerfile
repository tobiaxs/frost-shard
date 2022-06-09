FROM python:3.10.5-slim-buster as base

# Expose port
EXPOSE 8000

WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

# Add poetry path variable
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install necessary soft
RUN apt-get update \
    && apt-get install --no-install-recommends -y netcat curl git make gcc postgresql python3-dev libpq-dev \
    && apt-get clean

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Configure poetry
RUN poetry config virtualenvs.create false

# Local development
FROM base as dev

ENV DEVELOPMENT=1

# Copy & install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY . .

CMD ["bash", "docker/run.sh"]

# Production environment
FROM base as prod

RUN useradd -mr frostshard

USER frostshard

ENV PATH=$PATH:/home/frostshard/.local/bin

COPY --chown=frostshard:frostshard poetry.lock pyproject.toml ./
RUN poetry install --no-dev

COPY --chown=frostshard:frostshard . .

CMD ["bash", "docker/run.sh"]
