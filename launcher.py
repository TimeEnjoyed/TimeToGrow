import asyncio

import asqlite
import uvicorn

from api import Server
from bot import Bot


# main loop: asyncio event loop
# i need to be able to run two tasks:
# uvicorn = server that Starlette runs on
# twitchio = framework interacting with client


# Opens .env file

async def main() -> None:
    async with asqlite.create_pool('database/database.db') as pool:  # a statement called Context Manager (CM)
        await setup_database(pool)
        bot: Bot = Bot(pool=pool)  # instantiates TwitchIO bot
        app: Server = Server(bot=bot, pool=pool)  # instantiates Starlette server, and connects to TwitchIO bot
        bot.server = app  # the bots attribute 'self.server' is now the 'app'
        config: uvicorn.Config = uvicorn.Config(app, port=8000)
        server: uvicorn.Server = uvicorn.Server(config)
        asyncio.create_task(bot.start())
        await server.serve()


async def setup_database(pool) -> None:
    async with pool.acquire() as connection:
        # ^ We use CM so that the connection automatically closes when we're done with it
        with open('database/SCHEMA.sql') as schema:
            await connection.executescript(schema.read())

        print('Database setup complete')

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Closing down Bot and Server due to KeyboardInterrupt')

