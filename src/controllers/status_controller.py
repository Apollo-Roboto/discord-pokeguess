import psutil
from discord.ext import commands
from discord import app_commands, Interaction
from models.status import Status
from views import status_view

class StatusController(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		name='ping',
	)
	async def ping_command(self, ctx):
		print('Ping received')
		await ctx.send('Pong')

	@app_commands.command(
		name='status',
		description='Display bot status',
	)
	async def status_command(self, interaction: Interaction) -> None:

		status = Status(
			ready=True,
			ram=psutil.virtual_memory().percent,
			cpu=psutil.cpu_percent(1),
		)

		embed = status_view.StatusEmbed(status)

		await interaction.response.send_message(embed=embed)
