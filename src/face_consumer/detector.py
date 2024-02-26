import io
import uuid
from typing import Optional, List

import cv2
import numpy as np
from fastapi import UploadFile

from face_utils.entites import ImageFaceJobEntity
from face_utils.exceptions import DetectorException
from face_utils.settings import SETTINGS
from face_utils.storage import dir_bucket_storage


FACE_CLASSIFIER = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


class FaceDetector:
    DEFAULT_EXTENSION = "png"

    def __init__(self, face_job: ImageFaceJobEntity):
        self._face_job = face_job
        self._input_img = None
        self._faces = None

    async def _get_input_img(self) -> None:
        try:
            origin_file = await dir_bucket_storage.retrieve_file(
                filename=self._face_job.origin_filename,
                bucket_name=SETTINGS.origin_images_bucket_name,
            )
        except ValueError as exc:
            raise DetectorException("origin file for face job does not exists") from exc

        try:
            d = np.frombuffer(origin_file.file, dtype=np.uint8)
            self._input_img = cv2.imdecode(d, cv2.IMREAD_COLOR)
        except Exception as exc:
            raise DetectorException("invalid origin file for face job") from exc

    def _detect_faces(self) -> None:
        input_gray_img = cv2.cvtColor(self._input_img, cv2.COLOR_BGR2GRAY)
        self._faces = FACE_CLASSIFIER.detectMultiScale(
            input_gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

    def _convert_img_to_upload_file(self, img) -> UploadFile:
        is_success, buffer = cv2.imencode(
            f".{self.DEFAULT_EXTENSION}", img
        )
        if not is_success:
            raise DetectorException("internal error for processed img")
        return UploadFile(
            file=io.BytesIO(buffer), filename=f"new_{str(uuid.uuid4())}.png"
        )

    async def process(self) -> None:
        await self._get_input_img()
        self._detect_faces()
        if self.is_faces_detected:
            for x, y, w, h in self.faces_coordinates:
                cv2.rectangle(self._input_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    @property
    def faces_coordinates(self) -> Optional[List]:
        return [f.tolist() for f in self._faces]

    @property
    def is_faces_detected(self) -> bool:
        return len(self._faces) > 0

    @property
    def processed_img(self) -> Optional[UploadFile]:
        if not self.is_faces_detected:
            return None

        if self._input_img is not None:
            return self._convert_img_to_upload_file(img=self._input_img)

        raise ValueError("call process first")
