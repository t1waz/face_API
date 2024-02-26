import datetime
import re
import uuid

from fastapi import UploadFile

from face_backend.core.producer import ImageFaceJobProducer, image_face_job_producer
from face_utils import constants
from face_utils.entites import ImageFaceJobEntity
from face_utils.exceptions import JobException, ValidationException
from face_utils.repositories import (
    ImageFaceJobRepository,
    image_face_job_repository,
)
from face_utils.settings import SETTINGS
from face_utils.storage import dir_bucket_storage, DirBucketStorage


class ImageFaceJobService:
    ACCEPTED_MIME_TYPE_REGEX = r"image\/.*"

    def __init__(
        self,
        job_producer: ImageFaceJobProducer,
        file_storage: DirBucketStorage,
        job_repository: ImageFaceJobRepository,
    ) -> None:
        self._job_producer = job_producer
        self._file_storage = file_storage
        self._job_repository = job_repository

    def _validate_file(self, file: UploadFile) -> None:
        if not re.match(self.ACCEPTED_MIME_TYPE_REGEX, file.content_type):
            raise ValidationException(
                msg="invalid file, not a image, or invalid content_type"
            )

    async def get_job_processed_image(self, job_id: str) -> UploadFile:
        face_job = await self._job_repository.get(obj_id=job_id)
        if not face_job:
            raise JobException(msg="invalid job_id", is_critical=True)

        if face_job.state == constants.ImageFaceJobState.PENDING:
            raise JobException(msg="job not finished", is_critical=False)

        if face_job.state == constants.ImageFaceJobState.ERROR:
            raise JobException(msg="job error")

        if not face_job.processed_filename:
            raise JobException(msg="processed file not exist", is_critical=True)

        return await self._file_storage.retrieve_file(
            filename=face_job.processed_filename,
            bucket_name=SETTINGS.processed_images_bucket_name,
        )

    async def create_job_for_file(self, file: UploadFile) -> ImageFaceJobEntity:
        self._validate_file(file=file)

        origin_filename = await dir_bucket_storage.save_file(
            file=file,
            bucket_name=SETTINGS.origin_images_bucket_name,
        )

        job = ImageFaceJobEntity(
            id=uuid.uuid4(),
            is_face_detected=False,
            processed_filename=None,
            origin_filename=origin_filename,
            created_at=datetime.datetime.now(),
            modified_at=datetime.datetime.now(),
            state=constants.ImageFaceJobState.PENDING,
        )

        await self._job_repository.save(obj=job)

        await self._job_producer.produce(image_face_job=job)

        return job


image_face_job_service = ImageFaceJobService(
    file_storage=dir_bucket_storage,
    job_producer=image_face_job_producer,
    job_repository=image_face_job_repository,
)
