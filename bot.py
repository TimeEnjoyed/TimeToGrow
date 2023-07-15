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
from __future__ import annotations

import datetime
import os
import time
from typing import TYPE_CHECKING, Dict, Any

import asqlite
import twitchio
from dotenv import load_dotenv
from twitchio.ext import commands, pubsub, routines

from plant import Plant

if TYPE_CHECKING:
    from api import Server

# main loop: asyncio event loop
# i need to be able to run two tasks:
# uvicorn = server that Starlette runs on
# twitchio = framework interacting with client


# Opens .env file

load_dotenv(".env")

# Assigns secret access token to "token".
token: str = os.environ["ACCESS_TOKEN"]  # timetogrow_ permissions, generated with tokengenerator
CLIENT_ID: str = os.environ["CLIENT_ID"]  # timetogrow_ app
CLIENT_SECRET: str = os.environ["CLIENT_SECRET"]  # timetogrow_ app

epoch: datetime.datetime = datetime.datetime.utcfromtimestamp(0)
bot_name: str = "timetogrow_"
user_channel: str = os.environ["TEST_CHANNEL"]  # add your channel name to .env file for testing purposes


class Bot(commands.Bot):
    def __init__(self, pool: asqlite.Pool):
        # Initialize bot with access token, prefix, and a list of channels to join on boot.
        # prefix can be a callable, which returns a list of strings or a strings
        # initial_channels can also be callable

        super().__init__(token, prefix="!", initial_channels=[user_channel])

        self.server: Server | None = None  # adds the app to the bot
        self.pool = pool
        self.pubsub: pubsub.PubSubPool = pubsub.PubSubPool(self)  # thanks Mysty
        self.topics: list[pubsub.Topic] | None = None

    async def event_ready(self) -> None:
        # Is logged in and ready to use commands
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

        await self.pubsub.subscribe_topics(self.topics)

    async def event_message(self, message: twitchio.Message) -> None:
        assert self.server
        self.server.dispatch(data={"message": message.content, "user": message.author.name})

        # example of adding something to database:
        async with self.pool.acquire() as connection:
            # below format is sanitized inserts. (not f-string or .format)
            # anytime we deal with database, us $1 format
            await connection.execute("INSERT INTO messages(content) VALUES($1)", message.content)

    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage) -> None:
        assert self.server

        reward: twitchio.CustomReward = event.reward

        text_input: twitchio.CustomReward = event.input
        username: twitchio.PartialUser | None = event.user.name
        cycle: int = 1
        water: bool = False
        sabotage: bool = False
        growth_cycle: int | None = 1

        print(f"{reward} and input: {text_input}")
        self.server.dispatch(data={"username": username, "reward": reward})

        if reward.title == 'PLANT SEED':
            async with self.pool.acquire() as connection:
                print('connection established with sqlite database')
                # below format is sanitized inserts. (not f-string or .format)
                # anytime we deal with database, us $1 format
                await connection.execute(
                    "INSERT INTO plants(username, cycle, water, sabotage, growth_cycle) VALUES($1, $2, $3, $4, $5)",
                    username.lower(), cycle, water, sabotage, growth_cycle
                )

    # self.server.dispatch({"operation": "step"})

    ## GAME LOGIC BELOW ##
    ## sends data {'operation': 'step'} ##
    # @routines.routine(minutes=6)
    # def update_state(self):
    #     @routines.routine(minutes=1)
    #     def update_live():
    #         state = None
    #         state += 1
