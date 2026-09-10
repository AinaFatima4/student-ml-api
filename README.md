# student-ml-api

A small FastAPI prediction service used to demonstrate a professional MLOps
workflow: feature branches, Pull Requests, GitHub Actions CI, Docker
containerisation, semantic versioning and container-registry publishing.

## Endpoints

| Method | Path       | Description                       |
| ------ | ---------- | --------------------------------- |
| GET    | `/health`  | Liveness and version information  |
| POST   | `/predict` | Returns `value * 2`               |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install --requirement requirements-dev.txt
python -m pytest
uvicorn app:application --host 0.0.0.0 --port 5000
```

## Run with Docker

```bash
docker build --tag student-ml-api:1.0.0 .
docker run --detach --name student-ml-api --publish 5000:5000 student-ml-api:1.0.0
curl http://localhost:5000/health
```

## Workflow

```
feature branch -> Pull Request -> CI -> review -> merge -> tag -> release -> registry
```
