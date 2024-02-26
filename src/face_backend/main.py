from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse
from starlette.routing import WebSocketRoute
from tortoise import Tortoise, connections

from face_backend.core.services import image_face_job_service
from face_backend.views.jobs.schemas import CreateFaceJobSchema
from face_backend.views.jobs.views import jobs_router
from face_backend.views.jobs.ws import FaceJobEcho
from face_utils.db import TORTOISE_CONFIG
from face_utils.exceptions import (
    JobException,
    RepositoryException,
    StorageException,
    ValidationException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    yield

    await connections.close_all()


app = FastAPI(
    docs_url="/docs", routes=[WebSocketRoute("/ws", FaceJobEcho)], lifespan=lifespan
)
app.include_router(jobs_router, tags=["jobs"])


@app.exception_handler(JobException)
async def handle_job_exception(
    request: Request,  # type: ignore
    exc: JobException,
):
    if exc.is_critical:
        status_code = 204
    else:
        status_code = 202

    return JSONResponse(
        status_code=status_code,
        content={
            "reason": exc.msg,
        },
    )


@app.exception_handler(RepositoryException)
async def handle_repository_exception(
    request: Request,  # type: ignore
    exc: RepositoryException,
):
    return JSONResponse(
        status_code=400,
        content={
            "reason": exc.msg,
        },
    )


@app.exception_handler(StorageException)
async def handle_repository_exception(
    request: Request,  # type: ignore
    exc: StorageException,
):
    return JSONResponse(
        status_code=400,
        content={
            "reason": exc.msg,
        },
    )


@app.exception_handler(ValidationException)
async def handle_repository_exception(
    request: Request,  # type: ignore
    exc: StorageException,
):
    return JSONResponse(
        status_code=400,
        content={
            "reason": exc.msg,
        },
    )


@app.post("/image", status_code=201, response_model=CreateFaceJobSchema)
async def create_face_job(file: UploadFile) -> Dict:
    face_job = await image_face_job_service.create_job_for_file(file=file)

    return face_job.as_dict

@app.get("/health")
def health_check():
    return {"status": "ok"}
