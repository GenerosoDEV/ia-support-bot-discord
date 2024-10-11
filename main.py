import dotenv, discord, os, asyncio
from discord.ext import commands
from discord import app_commands


client = commands.Bot("g!", intents=discord.Intents.all())

client.remove_command("help")
dotenv.load_dotenv()

@client.event
async def on_ready():
    print(f"\n\nID: {client.user.id}\nNome: {client.user}")
    await app_commands.CommandTree.sync(client.tree)
    print("Slash commands sincronizados!")
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Gringa RP - Suporte Computacional!"))

async def main():
    async with client:
        folders = ["events", "commands"]
        for folder in folders:
            for file in os.listdir(f"./{folder}"):
                if file.endswith(".py") and file != "__init__.py":
                    cog = f"{folder}.{file[:-3]}"
                    try:
                        await client.load_extension(cog)
                    except Exception as e:
                        exc = '{}.{}'.format(type(e).__name__, e)
                        print(f'Falha ao carregar o(a) {cog}. Motivo: {exc}')
                    else:
                        print(f"{cog} carregado com sucesso!")
        await client.start(os.getenv("TOKEN"))

asyncio.run(main())
