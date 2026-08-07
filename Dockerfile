FROM python:3.13-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY personal_project/pyproject.toml personal_project/uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD ["uv", "run", "uvicorn", "personal_project.main:app", "--host", "0.0.0.0", "--port", "8000"]