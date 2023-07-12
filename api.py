"""
MIT License

Copyright (c) 2023 TimeEnjoyed, ezstarr, EvieePy, teabunniecodes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import asyncio
import json
import secrets
from typing import Any

import aiohttp
from sse_starlette import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from bot import CLIENT_ID, CLIENT_SECRET


class Server(Starlette):

    def __init__(self, *, bot, pool) -> None:  # we pass bot to Server when we instantiate it in launcher.py
        super().__init__(  # calls __init__ on Starlette
            routes=[
                # listen at endpoint. if we receive matching list of methods, we call the function
                Route('/oauth', self.oauth_endpoint, methods=['GET']),
                Route('/event', self.event_endpoint, methods=['GET']),
                Route('/test', self.test_endpoint, methods=['GET']),
                Mount('/images', app=StaticFiles(directory='website/static/images'), name='images'),
                Mount('/html', app=StaticFiles(directory='website/templates', html="base"))  # Allows index.html to be launched through starlette

            ],
            on_startup=[self.on_ready]
        )
        self._listeners: dict[str, asyncio.Queue] = {}
        self.bot = bot
        self.pool = pool

    async def on_ready(self) -> None:
        print('Server is ready!')

    def dispatch(self, data: dict[Any, Any]) -> None:
        asyncio.create_task(self._dispatch(data))

    async def _dispatch(self, data: dict[Any, Any]) -> None:
        for queue in self._listeners.values():
            await queue.put(data)

    async def event_endpoint(self, request: Request) -> EventSourceResponse:
        identifier: str = secrets.token_urlsafe(12)
        self._listeners[identifier] = asyncio.Queue()

        return EventSourceResponse(self.process_event(identifier=identifier, request=request))

    async def process_event(self, identifier: str, request: Request) -> None:
        queue: asyncio.Queue = self._listeners[identifier]

        while True:
            try:
                data = await queue.get()
                yield json.dumps(data)
            except asyncio.CancelledError:
                break

            if await request.is_disconnected():
                break

        del self._listeners[identifier]

    async def test_endpoint(self, request: Request) -> Response:
        async with self.pool.acquire() as connection:
            data = await connection.fetchone("SELECT rowid, content from messages WHERE rowid=$1", 1)
            return JSONResponse(dict(data), status_code=200)
        # return JSONResponse({"connected_to": [c.name for c in self.bot.connected_channels]}, status_code=200)

    async def oauth_endpoint(self, request: Request) -> Response:
        """
        Visit: https://dev.twitch.tv/console/apps/create
        Set OAuth Redirect URLs as: http://localhost:8000/oauth
        Choose a Category.
        Create App.
        Copy and Save ID and Secret.
        Visit your connect url E.g what you set in HTML with your required scopes: <a href="https://id.twitch.tv/oauth2/authorize?[parameters]">Connect with Twitch</a>
        For example: https://id.twitch.tv/oauth2/authorize?client_id=2hwtub5jvur3s1ww3ifb9047xnchpx&redirect_uri=http://localhost:8000/oauth&response_type=code&scope=chat:read
        """
        params = request.query_params
        code: str = params['code']

        client_id: str = ''  # client_id of app
        client_secret: str = ''  # client_secret of app
        grant: str = 'authorization_code'
        redirect: str = 'http://localhost:8000/oauth'

        url: str = f'https://id.twitch.tv/oauth2/token?' \
                   f'client_id={CLIENT_ID}&' \
                   f'client_secret={CLIENT_SECRET}&' \
                   f'code={code}&' \
                   f'grant_type={grant}&' \
                   f'redirect_uri={redirect}'

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as resp:
                if resp.status != 200:
                    return Response(status_code=500)

                data: dict[str, Any] = await resp.json()

                token: str = data['access_token']
                refresh_token: str = data['refresh_token']

        return JSONResponse({'token': data['access_token'], 'refresh': data['refresh_token']})
