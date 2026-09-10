"""student-ml-api

A minimal FastAPI inference service used to demonstrate a professional
MLOps workflow: pull requests, continuous integration, containerisation,
semantic versioning and container-registry publishing.
"""

from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictFloat, StrictInt

APPLICATION_NAME = "student-ml-api"
PREDICTION_MULTIPLIER = 2


def read_application_version() -> str:
    """Read the semantic version from the VERSION file next to this module.

    Keeping the version in a single file means the application, the Git tag
    and the Docker image tag can never drift apart.
    """
    version_file_path = Path(__file__).resolve().parent / "VERSION"
    if version_file_path.exists():
        return version_file_path.read_text(encoding="utf-8").strip()
    return "0.0.0"


APPLICATION_VERSION = read_application_version()

application = FastAPI(
    title=APPLICATION_NAME,
    version=APPLICATION_VERSION,
    description="Simple prediction API for the Advanced MLOps exercise.",
)


class PredictionRequest(BaseModel):
    """Request body for POST /predict.

    StrictInt and StrictFloat reject values such as the string "10".
    Without strict types, Pydantic would silently coerce "10" into 10 and
    the 'invalid input' test could never fail.
    """

    value: Union[StrictInt, StrictFloat]


class PredictionResponse(BaseModel):
    """Response body for POST /predict."""

    input: Union[StrictInt, StrictFloat]
    prediction: Union[StrictInt, StrictFloat]


@application.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """Translate FastAPI's default 422 validation error into a 400 response.

    A 400 Bad Request is the clearer contract for a public API, and it gives
    the automated tests a single, predictable status code to assert on.
    """
    error_details = []
    for validation_error in exception.errors():
        field_location = ".".join(
            str(location_part) for location_part in validation_error["loc"]
        )
        error_details.append(
            {
                "field": field_location,
                "message": validation_error["msg"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "invalid_request", "details": error_details},
    )


@application.get("/health")
def get_health_status() -> dict:
    """Liveness endpoint used by Docker, CI and the rollback demonstration."""
    return {
        "status": "healthy",
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
    }


@application.post("/predict", response_model=PredictionResponse)
def create_prediction(prediction_request: PredictionRequest) -> PredictionResponse:
    """Return a deterministic prediction for the supplied numeric value."""
    predicted_value = prediction_request.value * PREDICTION_MULTIPLIER
    return PredictionResponse(
        input=prediction_request.value,
        prediction=predicted_value,
    )


if __name__ == "__main__":
    import uvicorn

    # host="0.0.0.0" is mandatory inside a container. Binding to 127.0.0.1
    # would make the service unreachable from outside the container.
    uvicorn.run("app:application", host="0.0.0.0", port=5000)
