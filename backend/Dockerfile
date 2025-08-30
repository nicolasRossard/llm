FROM python:3.12-slim

RUN python --version && pip --version

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .


RUN pip install uv

# See https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy



# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/app/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY ./backend/ /app/backend/

RUN --mount=type=cache,target=/app/.cache/uv \
    uv sync --frozen --no-dev

#COPY .venv .
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/backend/:$PYTHONPATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []
# uncomment when creating revisions with alembic, so that alembic finds the script

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
