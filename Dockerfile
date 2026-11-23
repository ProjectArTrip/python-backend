FROM python:3.14-slim AS requirements-stage
WORKDIR /tmp
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir poetry==2.4.3 poetry-plugin-export
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.14-slim AS develop-stage
WORKDIR /app
COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app/app PYTHONUNBUFFERED=1
CMD ["uvicorn", "arttrip.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM develop-stage AS production-stage
COPY app /app/app
CMD ["uvicorn", "arttrip.main:app", "--host", "0.0.0.0", "--port", "8000"]