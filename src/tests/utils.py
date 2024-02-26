import datetime
from face_backend.main import app
from face_utils import constants


async def wait_for_job_finish(test_client, job_id: str) -> None:
    _TIMEOUT = 5
    start_timestamp = datetime.datetime.now()
    while datetime.datetime.now() < start_timestamp + datetime.timedelta(
        seconds=_TIMEOUT
    ):
        response = await test_client.get(
            app.url_path_for("get_face_job", face_job_id=job_id)
        )
        if (
            response.status_code == 200
            and response.json().get("state")
            == constants.ImageFaceJobState.FINISHED.value
        ):
            return

    raise ValueError("job wait timeout")
