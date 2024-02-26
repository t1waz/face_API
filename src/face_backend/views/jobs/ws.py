import asyncio
import uuid
from typing import Any

import redis.asyncio as redis
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from face_backend.pool import APP_REDIS_POOL
from face_utils.settings import SETTINGS
from face_utils.streams import RedisStreamHandler


class FaceJobEcho(WebSocketEndpoint):
    encoding = "json"

    def __init__(self, *args, **kwargs) -> None:
        self._task = None
        self._ws_stream_handler = None
        self._connection_id = str(uuid.uuid4())

        super().__init__(*args, **kwargs)

    async def _handle_stream_data(self, websocket: WebSocket) -> None:
        data = await self._ws_stream_handler.iter_read()
        if data:
            await websocket.send_json({"connection_id": self._connection_id, **data})

    async def _handle_websocket(
        self,
        websocket: WebSocket,
    ) -> None:
        while True:
            await self._handle_stream_data(websocket=websocket)
            await asyncio.sleep(1)

    async def send_updates(self, websocket: WebSocket):
        self._ws_stream_handler = RedisStreamHandler(
            conn=redis.Redis.from_pool(APP_REDIS_POOL),
            stream_name=SETTINGS.ws_stream_name,
        )

        try:
            await self._handle_websocket(websocket=websocket)
        except asyncio.CancelledError:
            await self._ws_stream_handler.destroy()

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        self._task = asyncio.create_task(self.send_updates(websocket))

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        await self._handle_stream_data(websocket=websocket)

    async def on_disconnect(self, websocket, close_code):
        self._task.cancel()
