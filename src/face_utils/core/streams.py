from typing import Optional, Dict


class StreamHandler:
    async def iter_read(self) -> Optional[Dict]:
        pass

    async def write(self, data) -> Optional[Dict]:
        pass


class StreamWorker:
    @classmethod
    async def setup_group(cls, *args, **kwargs):
        raise NotImplementedError

    async def push_to_stream(self, data: Dict) -> None:
        raise NotImplementedError

    async def read_from_stream(self) -> Optional[Dict]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError
