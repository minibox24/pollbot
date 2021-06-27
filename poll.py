import uuid
from itertools import chain

import discord
from discord.ext import commands
from discord.http import Route
from tortoise import Tortoise

from model import PollData
from utils import (
    dump_data,
    make_buttons,
    parse_components,
    parse_data,
    parse_db_data,
    parse_msg,
)


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state = bot._connection
        self.cache = {}

    @commands.command("종료")
    @commands.is_owner()
    async def exit_bot(self, ctx):
        await ctx.send("봇을 종료합니다.")
        await Tortoise.close_connections()
        self.bot.logout()
        exit()

    @commands.command("poll", aliases=["투표"])
    async def poll(self, ctx, title=None, *elements):
        if not title:
            return await ctx.reply("제목을 입력해주세요.")

        if not elements:
            return await ctx.reply("항목을 입력해주세요.")

        embed = discord.Embed(
            title=title,
            description="\n".join(map(lambda x: f"`{x}` : 0표", elements)),
            color=0x58D68D,
        )

        await self.bot.http.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=ctx.channel.id),
            json={
                "embed": embed.to_dict(),
                "components": make_buttons(
                    elements, dump_data([[] for _ in range(len(elements))])
                ),
            },
        )

    @commands.command("open", aliases=["개표"])
    async def open(self, ctx):
        if not ctx.message.reference:
            return await ctx.send("개표할 투표 메시지의 답장으로 이 커맨드를 사용해주세요.")

        message = await self.bot.http.request(
            Route(
                "GET",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=ctx.channel.id,
                message_id=ctx.message.reference.message_id,
            ),
        )

        components = parse_components(message["components"])

        data = parse_data(components)

        if data == "DB":
            print(message["embeds"])
            poll_data = await PollData.filter(
                id=message["embeds"][0]["footer"]["text"]
            ).first()
            data = parse_db_data(poll_data.data)
        elif not data:
            return await ctx.send("이 메시지는 투표 메시지가 아닌 것 같아요.")

        embed = discord.Embed(title=message["embeds"][0]["title"], color=0x58D68D)

        for element in components:
            users = data[element["index"]]
            usernames = []

            for i in users:
                if self.cache.get(i):
                    usernames.append(self.cache[i])
                else:
                    user = await self.bot.fetch_user(i)
                    self.cache[i] = str(user)
                    usernames.append(str(user))

            if not usernames:
                usernames = ["*아무도 없네요*"]

            embed.add_field(
                name=f"{element['label']} :: {len(users)}명", value="\n".join(usernames)
            )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        if msg["t"] != "INTERACTION_CREATE":
            return

        (
            message,
            user,
            custom_id,
            components,
            interaction_id,
            interaction_token,
        ) = parse_msg(msg["d"], self.state)

        self.cache[user.id] = str(user)

        poll_id = None
        data = parse_data(components)

        if data == "DB":
            poll_data = await PollData.filter(id=message.embeds[0].footer.text).first()
            poll_id = poll_data.id
            data = parse_db_data(poll_data.data)
        elif not data:
            return

        choose = list(filter(lambda x: x["id"] == custom_id, components))[0]

        if user.id in data[choose["index"]]:
            content = "투표를 취소했습니다!"
            data[choose["index"]].remove(user.id)
        elif user.id in list(chain.from_iterable(data)):
            index = list(filter(lambda x: user.id in x[1], enumerate(data)))[0][0]
            data[index].remove(user.id)
            data[choose["index"]].append(user.id)
            content = f"{components[index]['label']}에서 {choose['label']}(으)로 투표했습니다!"
        else:
            content = f"{choose['label']}에 투표했습니다!"
            data[choose["index"]].append(user.id)

        embed = message.embeds[0]
        embed.description = "\n".join(
            map(lambda x: f"`{x['label']}` : {len(data[x['index']])}표", components)
        )

        elements = list(map(lambda x: x["label"], components))
        dumped = dump_data(data)

        if not poll_id and len(elements) * 100 - 10 < len(dumped):
            poll_id = str(uuid.uuid4())
            embed.set_footer(text=poll_id)
            await PollData.create(id=poll_id, data=dumped)

        if poll_id:
            await PollData.filter(id=poll_id).update(data=dumped)
            dumped = ":POLL_DB:"

        await self.bot.http.request(
            Route(
                "PATCH",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=message.channel[0].id,
                message_id=message.id,
            ),
            json={
                "embed": embed.to_dict(),
                "components": make_buttons(elements, dumped),
            },
        )

        await self.bot.http.request(
            Route(
                "POST",
                "/interactions/{id}/{token}/callback",
                id=interaction_id,
                token=interaction_token,
            ),
            json={
                "type": 4,
                "data": {
                    "content": content,
                    "flags": 64,
                },
            },
        )


def setup(bot):
    bot.add_cog(Poll(bot))
