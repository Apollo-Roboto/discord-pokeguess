import logging
from discord.ext import commands
from discord.ext.commands import Context

log = logging.getLogger(__name__.removesuffix('_controller'))

class SyncController(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def sync(self, ctx: Context) -> None:
		log.info('syncing')
		async with ctx.typing():
			try:
				synced = await ctx.bot.tree.sync()
				log.info(f'Synced {len(synced)} commands ')
				await ctx.send(f'Synced {len(synced)} commands ')
			except:
				log.exception('error syncing')
				await ctx.send('error syncing')
