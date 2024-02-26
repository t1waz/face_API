import asyncio
from typing import Optional, List

from fastapi import UploadFile
from redis.asyncio import Redis

from face_consumer.detector import FaceDetector
from face_consumer.pool import CONSUMER_REDIS_POOL
from face_utils import constants
from face_utils.db import init
from face_utils.entites import ImageFaceJobEntity
from face_utils.exceptions import DetectorException
from face_utils.exceptions import RepositoryException
from face_utils.repositories import image_face_job_repository
from face_utils.settings import SETTINGS
from face_utils.storage import dir_bucket_storage
from face_utils.streams import RedisStreamWorker, RedisStreamHandler


CONSUMERS_PER_CONTAINER = 3


class ImageFaceJobProducer:
    def __init__(
        self, stream_worker: RedisStreamWorker, ws_stream_handler: RedisStreamHandler
    ) -> None:
        self._stream_worker = stream_worker

        self._stream_data: Optional[dict] = {}
        self._ws_stream_handler = ws_stream_handler
        self._image_face_job_id: Optional[str] = None
        self._image_face_job: Optional[ImageFaceJobEntity] = None

    async def _handle_ws_notification(self) -> None:
        await self._ws_stream_handler.write(
            data={
                "job_id": str(self._image_face_job.id),
                "processed_url": f"{SETTINGS.static_dir}/{self._image_face_job.processed_filename}",
            }
        )

    async def _handle_error_face_job(self):
        self._image_face_job.state = constants.ImageFaceJobState.ERROR
        await image_face_job_repository.update(obj=self._image_face_job)

    async def _handle_finished_face_job(
        self, process_image: Optional[UploadFile], faces_coordinates: Optional[List]
    ) -> None:
        if process_image:
            self._image_face_job.is_face_detected = True
            self._image_face_job.coordinates = faces_coordinates
            process_filename = await dir_bucket_storage.save_file(
                file=process_image, bucket_name=SETTINGS.processed_images_bucket_name
            )
            self._image_face_job.processed_filename = process_filename

        self._image_face_job.state = constants.ImageFaceJobState.FINISHED
        await image_face_job_repository.update(obj=self._image_face_job)

    async def _handle_image_face_job(self) -> None:
        # TODO - make all calls transactional in future
        detector = FaceDetector(face_job=self._image_face_job)
        try:
            await detector.process()
        except DetectorException:
            await self._handle_error_face_job()
            return

        await self._handle_finished_face_job(
            process_image=detector.processed_img,
            faces_coordinates=detector.faces_coordinates,
        )

        if detector.is_faces_detected:
            await self._handle_ws_notification()

    async def _get_image_face_job(self):
        self._stream_data = await self._stream_worker.read_from_stream()
        if not self._stream_data:
            return

        self._image_face_job_id = self._stream_data.get("id")
        if not self._image_face_job_id:
            self._image_face_job = None
            return
        try:
            self._image_face_job = await image_face_job_repository.get(
                obj_id=self._image_face_job_id
            )
        except RepositoryException:
            # ignore invalid msg, change if needed
            self._image_face_job = None

    async def _consume(self) -> None:
        await self._get_image_face_job()
        if not self.should_process:
            return None

        await self._handle_image_face_job()
        await self._stream_worker.ack_current_msg()

    def _clear(self) -> None:
        self._stream_data = {}
        self._image_face_job = None
        self._image_face_job_id = None

    async def start(self) -> None:
        while True:
            try:
                await self._consume()
                await asyncio.sleep(1)
            except Exception as exc:  # type: ignore
                # TODO - handle that whatever needed
                pass

            self._clear()

    @property
    def should_process(self) -> bool:
        try:
            return self._image_face_job is not None
        except ValueError:
            return False


async def run_consumers() -> None:
    await init()

    consumers = []
    for _ in range(CONSUMERS_PER_CONTAINER):
        worker = await RedisStreamWorker.setup_group(
            conn=Redis.from_pool(CONSUMER_REDIS_POOL),
            stream_name=SETTINGS.job_stream_name,
            group_name=SETTINGS.stream_group_name,
        )
        ws_stream_handler = RedisStreamHandler(
            conn=Redis.from_pool(CONSUMER_REDIS_POOL),
            stream_name=SETTINGS.ws_stream_name,
        )
        consumers.append(
            ImageFaceJobProducer(
                stream_worker=worker, ws_stream_handler=ws_stream_handler
            )
        )

    await asyncio.gather(*(consumer.start() for consumer in consumers))


if __name__ == "__main__":
    asyncio.run(run_consumers())
