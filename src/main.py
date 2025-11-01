import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
MAX_VOICE_MESSAGE_DURATION = int(os.getenv("MAX_VOICE_MESSAGE_DURATION", "60"))

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN not found in environment variables! Please set it in your .env file"
    )
if not DEEPL_API_KEY:
    raise ValueError(
        "DEEPL_API_KEY not found in environment variables! Please set it in your .env file"
    )


class Bot(commands.Bot):
    def __init__(self):
        # intents for the bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

    async def setup_hook(self) -> None:
        cogsLoaded = 0
        cogsCount = 0
        cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
        for cog_file in os.listdir(cogs_path):
            if cog_file.endswith(".py"):
                cogsCount += 1
                try:
                    print(f"Loading cog {cog_file}...")
                    await self.load_extension(f"cogs.{cog_file[:-3]}")
                    cogsLoaded += 1
                except Exception as e:
                    print(f"Failed to load cog {cog_file}: {e}")
        print(f"Loaded {cogsLoaded}/{cogsCount} cogs.")

        await self.tree.sync()
        print("Slash commands synced!")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("vmt is ready to transcribe and translate voice messages!")


bot = Bot()
bot.run(BOT_TOKEN)
