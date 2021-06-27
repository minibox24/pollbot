from discord.ext import commands
from tortoise import Tortoise


bot = commands.Bot(command_prefix="!")
bot.load_extension("poll")
bot.load_extension("jishaku")


@bot.event
async def on_ready():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["model"]})
    await Tortoise.generate_schemas()
    print("Ready")


bot.run("YOUR TOKEN")
