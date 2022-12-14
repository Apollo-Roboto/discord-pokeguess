from discord.ext import commands
from discord import app_commands, Interaction, File
from views import meta_view

class MetaController(commands.Cog):

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(
		name='invite',
		description='Invite this bot to your server!',
	)
	async def invite_command(self, interaction: Interaction) -> None:
		embed = meta_view.InviteEmbed(self.bot.user)
		view = meta_view.InviteView(self.bot.user)
		file = File('./pokemons/littlePokemonBanner.png')
		await interaction.response.send_message(view=view, file=file)
