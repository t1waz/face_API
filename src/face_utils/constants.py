import enum


class ImageFaceJobState(str, enum.Enum):
    PENDING = "pending"
    FINISHED = "finished"
    ERROR = "error"
