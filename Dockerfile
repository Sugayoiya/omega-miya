FROM python:3.11

# Configure Poetry
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --all-extras

# Run your app
COPY . /app
EXPOSE 3322
CMD ["poetry", "run", "python3", "bot.py"]

# run lagrange
# nohup ./Lagrange.OneBot >> ./output.log 2>&1 &
CMD {"nohup", "./Lagrange.OneBot", ">>", "./output.log", "2>&1", "&"}
