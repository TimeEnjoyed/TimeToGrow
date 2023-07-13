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
SOFTWARE.
"""

import asyncio
import os

import asqlite
from dotenv import load_dotenv
import uvicorn
from twitchio.ext import pubsub

from api import Server
from bot import Bot

# main loop: asyncio event loop
# i need to be able to run two tasks:
# uvicorn = server that Starlette runs on
# twitchio = framework interacting with client


# Opens .env file

load_dotenv(".env")
timeenjoyed_channel_id = 410885037

async def main() -> None:
    async with asqlite.create_pool("database/database.db") as pool:  # a statement called Context Manager (CM)
        await setup_database(pool)

        bot: Bot = Bot(pool=pool)  # instantiates TwitchIO bot
        app: Server = Server(bot=bot, pool=pool)  # instantiates Starlette server, and connects to TwitchIO bot
        bot.server = app  # the bots attribute 'self.server' is now the 'app

        bot.topics = [pubsub.channel_points(os.environ["OAUTH_ACCESS_TOKEN"])[timeenjoyed_channel_id]]

        config: uvicorn.Config = uvicorn.Config(app, port=8000)
        server: uvicorn.Server = uvicorn.Server(config)

        # start the keep alives
        asyncio.create_task(bot.start())
        await server.serve()


async def setup_database(pool: asqlite.Pool) -> None:
    async with pool.acquire() as connection:
        # ^ We use CM so that the connection automatically closes when we're done with it
        with open("database/SCHEMA.sql") as schema:
            await connection.executescript(schema.read())

        print("Database setup complete")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Closing down Bot and Server due to KeyboardInterrupt")
