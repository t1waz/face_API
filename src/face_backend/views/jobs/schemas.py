import datetime
import uuid
from typing import Optional

from face_backend.core.schemas import AppSchema
from face_utils import constants


class CreateFaceJobSchema(AppSchema):
    id: uuid.UUID
    created_at: datetime.datetime


class DetailedFaceJobSchema(AppSchema):
    id: uuid.UUID
    created_at: datetime.datetime
    modified_at: datetime.datetime
    state: constants.ImageFaceJobState
    coordinates: Optional[str] = None
    is_face_detected: Optional[bool] = False
    processed_filename: Optional[str] = None
