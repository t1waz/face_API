from typing import Optional, Dict

import redis.asyncio as redis

from face_backend.pool import APP_REDIS_POOL
from face_utils.entites import ImageFaceJobEntity
from face_utils.settings import SETTINGS
from face_utils.streams import RedisStreamWorker


PRODUCER_GROUP_NAME = "producer_group"


class ImageFaceJobProducer:
    def __init__(self, stream_worker: RedisStreamWorker) -> None:
        self._stream_worker = stream_worker
        self._job: Optional[ImageFaceJobEntity] = None

    def _serialize_image_face_job(self) -> Dict:
        return {"id": str(self.image_face_job.as_dict["id"])}

    async def produce(self, image_face_job: ImageFaceJobEntity) -> None:
        self._job = image_face_job
        await self._stream_worker.push_to_stream(
            data=self._serialize_image_face_job(),
        )

    @property
    def image_face_job(self) -> ImageFaceJobEntity:
        return self._job


image_face_job_producer = ImageFaceJobProducer(
    stream_worker=RedisStreamWorker(
        group_name=PRODUCER_GROUP_NAME,
        conn=redis.Redis.from_pool(APP_REDIS_POOL),
        stream_name=SETTINGS.job_stream_name,
    )
)
