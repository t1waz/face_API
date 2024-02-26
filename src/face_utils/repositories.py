import dataclasses
import uuid
from typing import Union

from tortoise.exceptions import OperationalError

from face_utils.core.repositories import Repository
from face_utils.entites import ImageFaceJobEntity
from face_utils.exceptions import RepositoryException
from face_utils.models import ImageFaceJobModel


class ImageFaceJobRepository(Repository):
    TABLE_MODEL = ImageFaceJobModel

    async def save(self, obj: ImageFaceJobEntity) -> None:
        table_obj = self.TABLE_MODEL(**obj.as_dict)
        await table_obj.save()

    async def update(self, obj: ImageFaceJobEntity) -> None:
        try:
            table_obj = await self.TABLE_MODEL.get(id=str(obj.id))
        except Exception as exc:
            raise ValueError("invalid obj") from exc

        for entity_attr in dataclasses.fields(obj):
            setattr(table_obj, entity_attr.name, getattr(obj, entity_attr.name))

        await table_obj.save()

    async def get(self, obj_id: Union[str, uuid.UUID]) -> ImageFaceJobEntity:
        try:
            table_obj = await self.TABLE_MODEL.get(id=str(obj_id))
        except OperationalError as exc:
            raise RepositoryException("invalid id") from exc

        return ImageFaceJobEntity(
            **{
                entity_attr.name: getattr(table_obj, entity_attr.name)
                for entity_attr in dataclasses.fields(ImageFaceJobEntity)
            }
        )


image_face_job_repository = ImageFaceJobRepository()
