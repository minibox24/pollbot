from discord.ext import commands


bot = commands.Bot(command_prefix="!")
bot.load_extension("poll")
bot.load_extension("jishaku")


@bot.event
async def on_ready():
    print("Ready")


bot.run("NTEyOTA2OTg4NDUyMTg0MDY0.W-5_2w.vnuBi9eYSOgIlSBH6OfIPoR4OWo")
