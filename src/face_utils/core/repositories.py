import uuid

from face_utils.entites import Entity


class Repository:
    TABLE_MODEL = None

    async def save(self, obj: Entity) -> None:
        raise NotImplementedError

    async def get(self, obj_id: uuid.UUID) -> Entity:
        raise NotImplementedError

    async def update(self, obj: Entity) -> None:
        raise NotImplementedError
