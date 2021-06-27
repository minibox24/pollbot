import discord
from discord.ext import commands
from discord.http import Route
from utils import dump_data, make_buttons


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        route = Route(
            "POST", "/channels/{channel_id}/messages", channel_id=ctx.channel.id
        )
        await self.bot.http.request(
            route,
            json={
                "embed": embed.to_dict(),
                "components": make_buttons(elements, dump_data([[] * len(elements)])),
            },
        )


def setup(bot):
    bot.add_cog(Poll(bot))
