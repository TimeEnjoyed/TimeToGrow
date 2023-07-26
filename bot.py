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
        self.rows: int = 10
        self.channel_store: dict[int, str] = {}
        self.update_state.start()
        # self.update_live.start()

    async def event_ready(self) -> None:
        # Is logged in and ready to use commands
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

        await self.pubsub.subscribe_topics(self.topics)

    async def event_message(self, message: twitchio.Message) -> None:
        if message.echo:
            return

        assert self.server
        # self.server.dispatch(data={"message": message.content, "user": message.author.name})

        # example of adding something to database:
        # async with self.pool.acquire() as connection:
        #     # below format is sanitized inserts. (not f-string or .format)
        #     # anytime we deal with database, us $1 format
        #     await connection.execute("INSERT INTO messages(content) VALUES($1)", message.content)
        await self.handle_commands(message)

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        print(error)

    @commands.command()
    async def water(self, ctx: commands.Context) -> None:
        async with self.pool.acquire() as connection:
            username = ctx.author.name.lower()
            try:
                user_plant = await connection.fetchone(
                    "SELECT cycle, water, sabotage, growth_cycle FROM plants WHERE username = ?", username)
                water_cycle, water, sabotage, growth_cycle = user_plant
            except:
                await ctx.send(f"{ctx.author.name} doesn't have a plant!")
                return
        if not sabotage and not water:  # sabotage = 0, water 0
            water = 1
            if growth_cycle <= 9:
                if water_cycle == 1: # initial cycle
                    if growth_cycle == 1: # first round to give the plant a sprout
                        growth_cycle += 1
                        await ctx.send(f"{ctx.author.name} watered their plant!")
                    else:
                        water_cycle = 2  # moves on but doesn't grow
                        await ctx.send(f"{ctx.author.name} watered their plant but it's a little early so the plant isn't thirsty yet!")
                elif water_cycle == 2:  # plant is thirsty and requires water
                    water_cycle = 1  # resets water cycle
                    growth_cycle += 1  # plant grows
                    await ctx.send(f"{ctx.author.name} watered their plant!")
                elif water_cycle == 3: # too late by a cycle
                    water_cycle = 2 # moves back to the growth cycle
                    await ctx.send(f"{ctx.author.name} watered their plant but it's too late so it won't grow this time!")
                elif water_cycle == 4: # plant already dead :(
                    await ctx.send(f"{ctx.author.name} plant is DEAD T_T!")
                    username = None
                    water_cycle = 1
                    water = 0
                    sabotage = 0
                    return
                await connection.execute("UPDATE plants SET cycle = ?, water = ?, growth_cycle = ? WHERE username = ?", water_cycle, water, growth_cycle, username)
        elif water:  # sabotage = 0, water is 1
            if water_cycle == 1 or water_cycle == 2 or water_cycle == 3:  # watered more than once in a cycle
                water_cycle = 3  # oopsies
                await ctx.send(f"{ctx.author.name} is drowning their plant")
            elif water_cycle == 4:
                await ctx.send(f"{ctx.author.name} drowned their plant!")

            await connection.execute("UPDATE plants SET cycle = ? WHERE username = ?", water_cycle, username)
        else: # plant was sabotaged before they could water
            await ctx.send(f"{ctx.author.name} plant is covered from the water!")
            # sabotage = 0
            # await connection.execute("UPDATE plants SET sabotage = ? WHERE username = ?", sabotage, username)
            return

    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage) -> None:
        assert self.server

        channel_info = self.channel_store.get(event.channel_id, None)
        if not channel_info:
            channel_info = (await self.fetch_channels([event.channel_id]))[0].user.name
            self.channel_store[event.channel_id] = channel_info
            channel = self.get_channel(channel_info)
        else:
            channel = self.get_channel(channel_info)
        print(channel)


        reward: twitchio.CustomReward = event.reward

        text_input: twitchio.CustomReward = event.input
        username: twitchio.PartialUser | None = event.user.name
        cycle: int = 1
        water: bool = False
        sabotage: bool = False
        growth_cycle: int | None = 1

        print(f"{reward} and input: {text_input}")
        # self.server.dispatch(data={"username": username, "reward": reward})

        if reward.title == 'PLANT SEED':
            async with self.pool.acquire() as connection:
                # print('connection established with sqlite database')
                # await channel.send(f"connection established with sqlite database")

                # retrieve current number of rows in plants table:
                count_rows_cursor = await connection.execute(
                    "SELECT COUNT(*) FROM plants")
                num_rows_tuple = await count_rows_cursor.fetchone()
                num_rows = num_rows_tuple[0]

                # retrieve rowid of null username:
                null_username_cursor = await connection.execute(
                    "SELECT rowid FROM plants WHERE username IS NULL LIMIT 1")
                avail_rowid_or_nonetype = await null_username_cursor.fetchone()

                # checks that database doesn't exceed certain size
                if num_rows < self.rows:
                    try:
                        # adds a new row to the table
                        await connection.execute(
                            "INSERT INTO plants(username, cycle, water, sabotage, growth_cycle) VALUES($1, $2, $3, $4, $5)",
                            username.lower(), cycle, water, sabotage, growth_cycle)
                    except:
                        await channel.send(f"{username} looks like you already have a plant")
                        # TODO: refund points

                else:
                    # checks for and retrieves available rowid for new username insertion
                    if avail_rowid_or_nonetype is not None:
                        avail_rowid = avail_rowid_or_nonetype[0]
                        # add person to plants table with available rowid
                        try:
                            await connection.execute(
                                "UPDATE plants SET username = $1, cycle = $2, water = $3, sabotage = $4, growth_cycle = $5 WHERE rowid = $6",
                                username.lower(), cycle, water, sabotage, growth_cycle, avail_rowid)
                        except Exception as e:
                            print(e)
                            await channel.send(f"{username} looks like you already have a plant")
                            # TODO: refund points
                    else:
                        await channel.send(f"{username}, sorry there are no spots left")

        if reward.title == 'SABOTAGE PLANT':
            async with self.pool.acquire() as connection:
                # print('connection established with sqlite database')

                # get water and sabotage status:
                try:
                    water_and_sabotage = await connection.fetchone(
                        "SELECT water, sabotage FROM plants WHERE username=$1", text_input)
                    water = water_and_sabotage[0]
                    sabotage = water_and_sabotage[1]

                    if username != text_input:
                        if water and not sabotage:
                            # checks if sabotage is true. if so, they've already been sabotaged
                            await channel.send(f"Sorry {username}, {text_input} watered their plant already")
                            # if sabotage is false, make it true, update database.
                        elif not water:
                            sabotage = 1
                            await channel.send(f"{text_input} has been sabotaged by {username}!")
                            await connection.execute(
                                "UPDATE plants SET sabotage = $1 WHERE username=$2",
                                sabotage, text_input)
                        elif sabotage:
                            await channel.send(f"Whoops {username}, {text_input} has been sabotaged already")
                    else:
                        await channel.send(f"Uhh, you want to sabotage yourself? Sorry you can't do that!")
                        return
                except Exception as e:
                    await channel.send(f"Nice try {username}, {text_input} doesn't have a plant to sabotage. Pay attention!")
                

    # GAME LOGIC BELOW ##
    # sends data {'operation': 'step'} ##
    @routines.routine(minutes=1)
    async def update_state(self):

        """This checks database
        changes the grow_cycle based on water, sabotage, and current grow_cycle.
        and dispatches json event"""

        assert self.server
        ground: list[dict] = []

        async with self.pool.acquire() as connection:
            # retrieve current number of rows in plants table:
            plant_table = await connection.execute(
                "SELECT * FROM plants")
            plant_rows = await plant_table.fetchall()

            # Get the number of rows using the len() function
            num_rows = len(plant_rows)

            # Print the resulting table
            print(f"Number of rows: {num_rows}")
            # for row in plant_rows:
            for row in plant_rows:
                plant: dict = {
                    "rowid": row[0],
                    "username": row[1],
                    "cycle": row[2],
                    "water": row[3],
                    "sabotage": row[4],
                    "growth_cycle": row[5]}
                
                ground.append(plant)
            # loop through old ground, add growth_cycle to it. IF.......
            for plant in ground:
                # print(plant)
                # first cycle, where (no water and no sabotage) --> moves onto cycle 2
                if plant['cycle'] == 1:
                    if not plant['water']:
                        plant['cycle'] = 2
                        if plant['sabotage']:
                            if plant['growth_cycle'] > 1:
                                plant['growth_cycle'] -= 1
                    # else:
                    #     if plant['growth_cycle'] == 1:
                    #         plant['growth_cycle'] += 1
                # second cycle, where plant is thirsty
                elif plant['cycle'] == 2:
                    if not plant['water']:
                        plant['cycle'] = 3
                        if plant['sabotage']:
                            if plant['growth_cycle'] > 1:
                                plant['growth_cycle'] -= 1
                # plant is about to die if you don't water it
                elif plant['cycle'] == 3:
                    if not plant['water']:
                        plant['cycle'] = 4
                        if plant['sabotage']:
                            if plant['growth_cycle'] > 1:
                                plant['growth_cycle'] -= 1
                elif plant['cycle'] == 4:
                    plant['username'] = None
        # async with self.pool.acquire() as connection:
                rowid = plant['rowid']
                username = plant['username']
                cycle = plant['cycle']
                # if cycle == 4:
                #     username = None
                growth_cycle = plant['growth_cycle']
                await connection.execute(
                    "UPDATE plants SET username = $1, cycle = $2, growth_cycle = $3 WHERE rowid = $6", username, cycle, growth_cycle, rowid)
                print(plant)
        print(f"its been 1 mins")
        self.server.dispatch(data=ground)
        # TODO something is happening around here where the growth cycle of index > 1 is adding to growth cycle even without them watering
        async with self.pool.acquire() as connection:
            for row in plant_rows:
                rowid = row[0]
                water = 0
                sabotage = 0
                await connection.execute(
                    "UPDATE plants SET water = $1, sabotage = $2 WHERE rowid = $3", water, sabotage, rowid)

        # await ctx.send(f"{ctx.author.name}data sent")

    # @routines.routine(minutes=1)
    # async def update_live(self):
    #     """Eventually updates wilt
    #     TODO after codejam is over
    #     """
    #     print(f"it's been 1 min")
