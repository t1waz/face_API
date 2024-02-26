import tempfile
import uuid

import pytest

from face_backend.main import app
from face_utils import constants
from face_utils.models import ImageFaceJobModel
from tests.utils import wait_for_job_finish


async def test_create_face_job_with_file_not_image_data(test_client):
    desired_filename = "test_1.png"

    with tempfile.TemporaryFile() as file:
        file.write(b"test")
        file.seek(0)
        response = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": (desired_filename, file, "text/plain")},
        )

    assert response.status_code == 400
    assert "content_type" in response.text


async def test_create_face_job_with_file_no_file_extension_in_name(test_client):
    desired_filename = "test_1"

    with open("/app/tests/data/face.png", "rb") as file:
        response = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": (desired_filename, file.read(), "image/png")},
        )

    assert response.status_code == 400
    assert "extension" in response.text


async def test_create_face_job_valid_data_with_face_create_face_job(test_client):
    desired_filename = "test_1.png"

    with open("/app/tests/data/face.png", "rb") as file:
        response = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": (desired_filename, file.read(), "image/png")},
        )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert await ImageFaceJobModel.filter(id=data["id"]).exists()


async def test_create_face_job_valid_data_no_face_create_face_job(test_client):
    desired_filename = "test_1.png"

    with open("/app/tests/data/no_face.png", "rb") as file:
        response = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": (desired_filename, file.read(), "image/png")},
        )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert await ImageFaceJobModel.filter(id=data["id"]).exists()


@pytest.mark.parametrize(
    "invalid_id",
    [
        123,
        3.14,
        "False",
        False,
        " ",
        "foo",
    ],
)
async def test_get_face_job_not_invalid_job_id(invalid_id, test_client):
    response = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=invalid_id)
    )

    assert response.status_code == 400


async def test_get_face_job_not_existing_job(test_client):
    response = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=str(uuid.uuid4()))
    )

    assert response.status_code == 400


async def test_get_face_job_existing_job(
    test_client,
    f_face_job_1,
):
    response = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=str(f_face_job_1.id))
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(f_face_job_1.id)
    assert data["state"] == f_face_job_1.state.value
    assert data["is_face_detected"] == f_face_job_1.is_face_detected


async def test_e2e_test_for_face_job_with_image_that_not_contains_face(test_client):
    with open("/app/tests/data/no_face.png", "rb") as file:
        response_1 = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": ("test_1.png", file.read(), "image/png")},
        )

    assert response_1.status_code == 201

    job_id = response_1.json()["id"]

    await wait_for_job_finish(test_client=test_client, job_id=job_id)

    response_2 = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=job_id)
    )

    assert response_2.status_code == 200

    data_2 = response_2.json()

    assert data_2["state"] == constants.ImageFaceJobState.FINISHED.value
    assert data_2["is_face_detected"] is False
    assert data_2["coordinates"] is None

    response_3 = await test_client.get(
        app.url_path_for("get_face_job_processed_image", face_job_id=job_id)
    )

    assert response_3.status_code == 400


async def test_e2e_test_for_face_job_with_image_that_contains_face(test_client):
    with open("/app/tests/data/face.png", "rb") as file:
        response_1 = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": ("test_1.png", file.read(), "image/png")},
        )

    assert response_1.status_code == 201

    job_id = response_1.json()["id"]

    await wait_for_job_finish(test_client=test_client, job_id=job_id)

    response_2 = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=job_id)
    )

    assert response_2.status_code == 200

    data_2 = response_2.json()

    assert data_2["state"] == constants.ImageFaceJobState.FINISHED.value
    assert data_2["is_face_detected"] is True
    assert data_2["coordinates"] == "[[110, 107, 265, 265]]"

    response_3 = await test_client.get(
        app.url_path_for("get_face_job_processed_image", face_job_id=job_id)
    )

    assert response_3.status_code == 200
