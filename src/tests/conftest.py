import asyncio
import datetime
import uuid

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from redis.asyncio import Redis

from face_backend.main import app
from face_utils import constants
from face_utils.db import init, get_redis_pool
from face_utils.entites import ImageFaceJobEntity
from face_utils.models import ImageFaceJobModel
from face_utils.settings import SETTINGS

TEST_REDIS_POOL = get_redis_pool()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

    loop.close()


@pytest.fixture(scope="session")
async def test_client() -> AsyncClient:  # type: ignore
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
async def ws_test_client(event_loop) -> AsyncClient:  # type: ignore
    yield TestClient(app=app)


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await init(generate_schemas=True)

    yield


@pytest.fixture(autouse=True)
async def clear_streams():
    conn = Redis.from_pool(TEST_REDIS_POOL)

    yield

    await conn.xtrim(name=SETTINGS.job_stream_name, maxlen=0)
    await conn.xtrim(name=SETTINGS.ws_stream_name, maxlen=0)
    await conn.aclose()


@pytest.fixture
async def f_face_job_1():
    face_job_1_data = {
        "id": uuid.uuid4(),
        "origin_filename": "foo.png",
        "processed_filename": None,
        "is_face_detected": False,
        "created_at": datetime.datetime.now(),
        "modified_at": datetime.datetime.now(),
        "state": constants.ImageFaceJobState.PENDING,
    }
    face_job_1 = await ImageFaceJobModel.create(**face_job_1_data)

    yield ImageFaceJobEntity(**face_job_1_data)

    await face_job_1.delete()
