import asyncio
import json

from face_backend.main import app
from face_utils.settings import SETTINGS
from tests.utils import wait_for_job_finish


async def test_it_is_possible_to_receive_echo_face_job_data(
    test_client, ws_test_client
):
    with open("/app/tests/data/face.png", "rb") as file:
        job_response = await test_client.post(
            app.url_path_for("create_face_job"),
            files={"file": ("test_1.png", file.read(), "image/png")},
        )

    assert job_response.status_code == 201

    job_response_data = job_response.json()

    await wait_for_job_finish(test_client=test_client, job_id=job_response_data["id"])

    with ws_test_client.websocket_connect("/faces") as websocket:
        websocket.send_text(json.dumps({"foo": "bar"}))
        ws_data = websocket.receive_json()

    assert "connection_id" in ws_data
    assert ws_data["processed_url"].startswith(SETTINGS.static_dir)

    job_id = ws_data["job_id"]
    ws_processed_filename = ws_data["processed_url"].split(f"{SETTINGS.static_dir}/")[1]

    job_response = await test_client.get(
        app.url_path_for("get_face_job", face_job_id=job_id)
    )

    assert job_response.status_code == 200

    job_data = job_response.json()

    assert job_data["id"] == ws_data["job_id"]
    assert job_data["is_face_detected"] is True
    assert job_data["processed_filename"] == ws_processed_filename
