from discord.ext import commands


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("ping")
    async def ping(self, ctx):
        await ctx.reply("pong")


def setup(bot):
    bot.add_cog(Poll(bot))
