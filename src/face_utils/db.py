import redis.asyncio as redis
from tortoise import Tortoise

from face_utils.settings import (
    SETTINGS,
    TORTOISE_CONFIG,
)


async def init(generate_schemas: bool = False):
    await Tortoise.init(config=TORTOISE_CONFIG)
    if generate_schemas:
        await Tortoise.generate_schemas()


def get_redis_pool():
    return redis.ConnectionPool.from_url(
        f"redis://{SETTINGS.redis_host}:{SETTINGS.redis_port}"
    )
