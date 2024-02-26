from tortoise import fields
from tortoise.models import Model

from face_utils import constants


class ImageFaceJobModel(Model):
    id = fields.UUIDField(pk=True)
    state = fields.CharEnumField(
        enum_type=constants.ImageFaceJobState,
        default=constants.ImageFaceJobState.PENDING,
    )
    origin_filename = fields.CharField(max_length=255)
    processed_filename = fields.CharField(max_length=255, null=True)
    is_face_detected = fields.BooleanField(default=False)
    coordinates = fields.CharField(max_length=256, null=True)
    modified_at = fields.DatetimeField(null=True, auto_now=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)
