import asyncio
import json

from sse_starlette import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class Server(Starlette):

    def __init__(self, *, bot, pool) -> None:  # we pass bot to Server when we instantiate it in launcher.py
        super().__init__(  # calls __init__ on Starlette
            routes=[
                # listen at endpoint. if we receive matching list of methods, we call the function
                Route('/send', self.send_endpoint, methods=['POST']),
                Route('/event', self.event_endpoint, methods=['GET']),
                Route('/test', self.test_endpoint, methods=['GET'])
            ],
            on_startup=[self.on_ready]
        )
        self.queue: asyncio.Queue = asyncio.Queue()
        self.bot = bot
        self.pool = pool

    async def on_ready(self) -> None:
        print('Server is ready!')

    async def send_endpoint(self, request: Request) -> Response:
        data = await request.json()
        await self.queue.put(data)
        return Response(status_code=200)

    async def event_endpoint(self, request: Request) -> EventSourceResponse:
        return EventSourceResponse(self.process_event(request=request))

    async def process_event(self, request: Request) -> None:
        while True:
            try:
                data = await self.queue.get()
                yield json.dumps(data)
            except asyncio.CancelledError:
                break
            if await request.is_disconnected():
                break

    async def test_endpoint(self, request: Request) -> Response:
        async with self.pool.acquire() as connection:
            data = await connection.fetchone("SELECT rowid, content from messages WHERE rowid=$1", 1)
            return JSONResponse(dict(data), status_code=200)
        # return JSONResponse({"connected_to": [c.name for c in self.bot.connected_channels]}, status_code=200)
