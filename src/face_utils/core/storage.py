from fastapi import UploadFile


class BucketStorage:
    async def save_file(self, file: UploadFile) -> str:
        raise NotImplementedError

    async def retrieve_file(self, filename: str, bucket_name: str = None) -> UploadFile:
        raise NotImplementedError
