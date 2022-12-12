from discord.ext import commands
from discord.ext.commands import Context

class SyncController(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.is_owner()
	async def sync(self, ctx: Context) -> None:
		print('syncing')
		try:
			synced = await ctx.bot.tree.sync()
			print(f'Synced {len(synced)} commands ')
			await ctx.send(f'Synced {len(synced)} commands ')
		except Exception as e:
			print('error syncing')
			print(e)
			await ctx.send('error syncing')
