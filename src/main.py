import logging
import asyncio
import os
import sys
from discord.ext import commands
from discord import Intents
from discord.ext.prometheus import PrometheusCog, PrometheusLoggingHandler
from dotenv import load_dotenv
import controllers

logging.basicConfig(
	stream=sys.stdout,
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S',
	format='%(levelname)s [ %(asctime)s ] %(name)s : %(message)s',
)
logging.getLogger().addHandler(PrometheusLoggingHandler())
log = logging.getLogger(__name__)

async def main():
	load_dotenv()

	bot = commands.AutoShardedBot(
		command_prefix='!',
		intents=Intents.all(),
		help_command=None,
	)

	await bot.add_cog(PrometheusCog(bot))

	await controllers.add_cogs(bot)

	print("App Commands:")
	for command in bot.tree.walk_commands():
		print(f'\t{command.name}')
	print("Commands:")
	for command in bot.walk_commands():
		print(f'\t{command.name}')

	await bot.start(os.environ['DISCORD_BOT_TOKEN'])

if __name__ == '__main__':
	asyncio.run(main())
