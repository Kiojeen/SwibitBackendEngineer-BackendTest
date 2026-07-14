FROM python:3.14-slim

RUN pip install uv

WORKDIR /app

COPY . .

RUN uv sync

CMD ["uv", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]