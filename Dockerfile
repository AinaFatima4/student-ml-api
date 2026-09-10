# Explicit base-image version. "python:latest" is forbidden because it makes
# builds non-reproducible: the same Dockerfile could produce different images.
FROM python:3.12-slim

# Build arguments are supplied by the release workflow so that the finished
# image can be traced back to the exact commit that produced it.
ARG APPLICATION_VERSION="0.0.0"
ARG GIT_COMMIT_SHA="unknown"
ARG BUILD_DATE="unknown"
ARG SOURCE_REPOSITORY="unknown"

# Open Container Initiative (OCI) standard labels, readable via docker inspect.
LABEL org.opencontainers.image.title="student-ml-api" \
      org.opencontainers.image.description="Student ML inference API" \
      org.opencontainers.image.version="${APPLICATION_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.source="${SOURCE_REPOSITORY}"

# PYTHONDONTWRITEBYTECODE stops .pyc files being written into the image.
# PYTHONUNBUFFERED makes logs appear immediately in "docker logs".
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /application

# Dependencies are copied and installed BEFORE the source code.
# requirements.txt changes rarely, so this layer is reused from cache on
# every build where only app.py changed.
COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

# Application source is copied last, in the layer that changes most often.
COPY VERSION .
COPY app.py .

# Run as an unprivileged user instead of root.
RUN useradd --create-home --shell /bin/bash application_user
USER application_user

EXPOSE 5000

# host 0.0.0.0 so the port published with -p is actually reachable.
CMD ["uvicorn", "app:application", "--host", "0.0.0.0", "--port", "5000"]
