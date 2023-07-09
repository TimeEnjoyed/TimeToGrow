import datetime
import os

import twitchio
from dotenv import load_dotenv
from twitchio.ext import commands

# main loop: asyncio event loop
# i need to be able to run two tasks:
# uvicorn = server that Starlette runs on
# twitchio = framework interacting with client


# Opens .env file

load_dotenv('.env')

# Assigns secret access token to "token".
token = os.environ['ACCESS_TOKEN']

epoch = datetime.datetime.utcfromtimestamp(0)
bot_name = "TheTimeBot"
user_channel = 'timeenjoyed'


class Bot(commands.Bot):
    def __init__(self, pool):
        # Initialize bot with access token, prefix, and a list of channels to join on boot.
        # prefix can be a callable, which returns a list of strings or a strings
        # initial_channels can also be callable

        super().__init__(token, prefix='!', initial_channels=[user_channel])
        self.server = None  # adds the app to the bot
        self.pool = pool


    async def event_ready(self):
        # Is logged in and ready to use commands
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        print(self.server)


    async def event_message(self, message: twitchio.Message) -> None:
        print(f'MESSAGE FROM: {message.author.name} - {message.content}')

        # example of adding something to database:
        async with self.pool.acquire() as connection:
            # below format is sanitized inserts. (not f-string or .format)
            # anytime we deal with database, us $1 format
            await connection.execute("INSERT INTO messages(content) VALUES($1)", message.content)

