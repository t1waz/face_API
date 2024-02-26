from __future__ import annotations

import json
import uuid
from typing import Dict, Optional

import redis
from redis.asyncio import Redis
from redis.exceptions import ResponseError

from face_utils.core.streams import StreamWorker, StreamHandler


class RedisStreamHandler(StreamHandler):
    def __init__(self, conn: Redis, stream_name: str) -> None:
        self._conn = conn
        self._last_msg_id = "0"
        self._stream_name = stream_name

    async def iter_read(self) -> Optional[Dict]:
        data = await self._conn.xread(
            count=1, block=10, streams={self._stream_name: self._last_msg_id}
        )
        if not data:
            return {}

        msg_id, data = data[0][1][0]
        self._last_msg_id = msg_id.decode()

        return {k.decode(): v.decode() for k, v in data.items()}

    async def write(self, data: Dict) -> None:
        await self._conn.xadd(self._stream_name, data)

    async def destroy(self) -> None:
        await self._conn.aclose()


class RedisStreamWorker(StreamWorker):
    GROUP_CREATE_ID = "0-0"

    def __init__(self, conn: Redis, stream_name: str, group_name: str) -> None:
        self._conn = conn
        self._current_msg = None
        self._group_name = group_name
        self._stream_name = stream_name
        self._name = str(uuid.uuid4())

    async def _get_stream_stats(self) -> Optional[Dict]:
        try:
            return await self._conn.xinfo_groups(self.stream_name)
        except (ValueError, AttributeError, ResponseError):
            return None

    @classmethod
    async def setup_group(
        cls, conn: Redis, stream_name: str, group_name: str
    ) -> RedisStreamWorker:
        instance = cls(conn=conn, stream_name=stream_name, group_name=group_name)

        try:
            await conn.xgroup_create(
                id="0-0",
                mkstream=True,
                name=stream_name,
                groupname=instance.group_name,
            )
        except redis.exceptions.ResponseError:
            pass

        return instance

    async def push_to_stream(self, data: Dict) -> None:
        await self._conn.xadd(self.stream_name, {"data": json.dumps(data)})

    async def ack_current_msg(self) -> None:
        await self._conn.xack(self.stream_name, self.group_name, self.current_msg_id)

    async def read_from_stream(self) -> Optional[Dict]:
        readed_data = await self._conn.xreadgroup(
            count=1,
            block=10,
            noack=False,
            consumername=self.name,
            groupname=self.group_name,
            streams={self.stream_name: ">"},
        )
        if readed_data:
            self._current_msg = readed_data
            return json.loads(readed_data[0][1][0][1][b"data"].decode())

        return None

    async def destroy(self) -> None:
        await self._conn.aclose()

    @property
    def name(self) -> str:
        return self._name

    @property
    def group_name(self) -> str:
        return self._group_name

    @property
    def stream_name(self) -> str:
        return self._stream_name

    @property
    def current_msg(self):
        return self._current_msg

    @property
    def current_msg_id(self) -> str:
        return self.current_msg[0][1][0][0]
