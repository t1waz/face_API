from typing import Optional


class AppException(Exception):
    def __init__(self, msg: str, is_critical: Optional[bool] = False) -> None:
        self._msg = msg
        self._is_critical = is_critical

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def is_critical(self) -> bool:
        return self._is_critical or False


class JobException(AppException):
    pass


class DetectorException(AppException):
    pass


class RepositoryException(AppException):
    pass


class StorageException(AppException):
    pass


class ValidationException(AppException):
    pass
