import discord
from discord.ext import commands
from discord.http import Route
from utils import dump_data, make_buttons, parse_msg, parse_data
from itertools import chain


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state = bot._connection

    @commands.command("ping")
    async def ping(self, ctx):
        await ctx.reply("pong")

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

        data = parse_data(components)

        if not data:
            return

        choose = list(filter(lambda x: x["id"] == custom_id, components))[0]

        if user.id in data[choose["index"]]:
            content = "투표를 취소했습니다!"
            data[choose["index"]].remove(user.id)
        elif user.id in list(chain.from_iterable(data)):
            index = list(filter(lambda x: user.id in x[1], enumerate(data)))[0][0]
            data[index].remove(user.id)
            data[choose["index"]].append(user.id)
            content = f"{components[index]['label']}에서 {choose['label']}로 투표했습니다!"
        else:
            content = f"{choose['label']}에 투표했습니다!"
            data[choose["index"]].append(user.id)

        embed = message.embeds[0]
        embed.description = "\n".join(
            map(lambda x: f"`{x['label']}` : {len(data[x['index']])}표", components)
        )

        await self.bot.http.request(
            Route(
                "PATCH",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=message.channel[0].id,
                message_id=message.id,
            ),
            json={
                "embed": embed.to_dict(),
                "components": make_buttons(
                    list(map(lambda x: x["label"], components)), dump_data(data)
                ),
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
