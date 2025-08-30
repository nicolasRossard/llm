FROM python:3.13-slim

RUN python --version && pip --version

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/app/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-default-groups --only-group front

COPY ./front/ /app/front/

RUN --mount=type=cache,target=/app/.cache/uv \
    uv sync --frozen --no-default-groups --only-group front

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/front/:$PYTHONPATH"

WORKDIR /app/front
# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []
CMD ["uv", "run", "--no-default-groups", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"]