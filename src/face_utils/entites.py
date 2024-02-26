import datetime
import uuid
from dataclasses import dataclass
from typing import Optional

from face_utils import constants
from face_utils.core.entities import Entity


@dataclass
class ImageFaceJobEntity(Entity):
    id: uuid.uuid4()
    created_at: datetime.datetime
    modified_at: datetime.datetime
    state: constants.ImageFaceJobState
    coordinates: Optional[str] = None
    origin_filename: Optional[str] = None
    processed_filename: Optional[str] = None
    is_face_detected: Optional[bool] = False
