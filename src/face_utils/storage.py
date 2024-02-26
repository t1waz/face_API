import os
import uuid

import aiofiles
from fastapi import UploadFile

from face_utils.core.storage import BucketStorage
from face_utils.exceptions import StorageException
from face_utils.settings import SETTINGS


class DirBucketStorage(BucketStorage):
    FILENAME_SPLITTER = "."
    STORAGE_DIR = SETTINGS.dir_bucket_files_dir

    @staticmethod
    def _create_bucket(bucket_path: str) -> None:
        bucket_dir_exists = os.path.exists(bucket_path)
        if not bucket_dir_exists:
            os.makedirs(bucket_path)

    def _get_file_kind_from_filename(self, filename: str) -> str:
        try:
            _, file_kind = filename.split(self.FILENAME_SPLITTER)
        except ValueError as exc:
            raise StorageException("invalid file extension")

        return file_kind

    def _get_file_id_from_filename(self, filename: str) -> str:
        file_id, _ = filename.split(self.FILENAME_SPLITTER)
        return file_id

    def _get_save_path(self, bucket_name: str = None):
        save_path = f"{self.STORAGE_DIR}"
        if bucket_name:
            save_path = f"{save_path}/{bucket_name}"

        return save_path

    def _get_filename(self, file_id: str, file_kind: str) -> str:
        return f"{file_id}{self.FILENAME_SPLITTER}{file_kind}"

    async def save_file(self, file: UploadFile, bucket_name: str = None) -> str:
        file_id = uuid.uuid4()
        save_path = self._get_save_path(bucket_name=bucket_name)
        file_kind = self._get_file_kind_from_filename(filename=file.filename)
        filename = self._get_filename(file_id=str(file_id), file_kind=file_kind)

        if bucket_name:
            self._create_bucket(bucket_path=save_path)

        async with aiofiles.open(f"{save_path}/{filename}", "wb") as out_file:
            while content := await file.read(1024):
                await out_file.write(content)

        return filename

    async def retrieve_file(self, filename: str, bucket_name: str = None) -> UploadFile:
        file_path = self._get_save_path(bucket_name=bucket_name)

        try:
            async with aiofiles.open(f"{file_path}/{filename}", "rb") as file:
                file = await file.read(-1)
        except FileNotFoundError as exc:
            raise StorageException("filename does not exists") from exc

        return UploadFile(file=file)  # type: ignore


dir_bucket_storage = DirBucketStorage()
