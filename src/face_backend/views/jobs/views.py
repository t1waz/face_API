from typing import Dict

from fastapi import APIRouter, UploadFile, Response

from face_backend.core.services import image_face_job_service
from face_backend.views.jobs.schemas import CreateFaceJobSchema, DetailedFaceJobSchema
from face_utils.repositories import image_face_job_repository


jobs_router = APIRouter(prefix="/jobs")


@jobs_router.get(
    "/{face_job_id}", status_code=200, response_model=DetailedFaceJobSchema
)
async def get_face_job(face_job_id: str) -> Response:
    return await image_face_job_repository.get(obj_id=face_job_id)


@jobs_router.get("/{face_job_id}/processed-image", status_code=200)
async def get_face_job_processed_image(face_job_id: str) -> Response:
    processed_image = await image_face_job_service.get_job_processed_image(
        job_id=face_job_id
    )

    return Response(content=processed_image.file, media_type="image/png")
