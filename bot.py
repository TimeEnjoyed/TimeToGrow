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
bot_name = "timetogrow_"
user_channel = os.environ['TEST_CHANNEL'] # add your channel name to .env file for testing purposes


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

