import logging
import asyncio
import os
import sys
from discord.ext import commands
from discord import Intents, Interaction, InteractionType
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

	intents = Intents()
	intents.members = True
	intents.guilds = True
	intents.guild_messages = True
	intents.message_content = True

	bot = commands.AutoShardedBot(
		command_prefix='!',
		intents=intents,
		help_command=None,
	)

	await bot.add_cog(PrometheusCog(bot))

	await controllers.add_cogs(bot)

	log.info("App Commands:")
	for command in bot.tree.walk_commands():
		log.info(f'\t{command.name}')
	log.info("Commands:")
	for command in bot.walk_commands():
		log.info(f'\t{command.name}')

	@bot.listen()
	async def on_interaction(interaction: Interaction):
		# command name can be None if comming from a view (like a button click)

		text = f'Interaction ({str(interaction.type.name)})'
		if interaction.type == InteractionType.application_command:
			text += f' {interaction.command.name} id:{interaction.data["id"]}'

		log.info(text)

	await bot.start(os.environ['DISCORD_BOT_TOKEN'])

if __name__ == '__main__':
	asyncio.run(main())
