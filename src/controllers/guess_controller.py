from datetime import datetime, timedelta
import random
import logging
from discord.ext import commands
from discord import app_commands, Interaction, File, Message
from discord.app_commands import Choice, Range
import discord
from models.guesser import Guesser
from views import guess_view
from services.guesser_service import GuesserService

log = logging.getLogger(__name__.removesuffix('_controller'))

class GuessController(commands.Cog):

	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.guesserService = GuesserService()

		# register the on_guess_end method to be called
		self.guesserService.on_guesser_end_event.append(self.on_guess_end)

	@app_commands.command(
		name='pokeguess',
		description='Start a Pokemon guess',
	)
	@app_commands.describe(
		generation='The Pokemon generation to play from',
		timeout='Guessing timeout in seconds'
	)
	@app_commands.choices(generation=[
		Choice(name='All', value=0),
		Choice(name='Generation 1', value=1),
		Choice(name='Generation 2', value=2),
		Choice(name='Generation 3', value=3),
		Choice(name='Generation 4', value=4),
		Choice(name='Generation 5', value=5),
		Choice(name='Generation 6', value=6),
		Choice(name='Generation 7', value=7),
		Choice(name='Generation 8', value=8),
	])
	async def pokeguess_command(self, interaction: Interaction, generation: Choice[int] = None, timeout: Range[int, 15, 300] = 60) -> None:

		# do I have permission to read and send messages here
		permissions = interaction.channel.permissions_for(interaction.guild.me)
		if permissions.read_messages == False or permissions.send_messages == False:
			log.info('Missing permissions on this channel')
			embed = guess_view.MissingPermissionsEmbed()
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		# is there a running guesser here?
		if self.guesserService.get_guesser(interaction.channel) != None:
			embed = guess_view.AlreadyActiveEmbed()
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return
		
		# max 5 minutes
		if timeout > 300:
			embed = guess_view.InvalidTimeoutEmbed()
			await interaction.response.send_message(embed=embed, ephemeral=True)
			return

		id_range = (0, 905)

		if generation == None:
			generation = Choice(name='All', value=0)
		
		if generation.value == 0: # all
			id_range = (0, 905)
		elif generation.value == 1:
			id_range = (0, 151)
		elif generation.value == 2:
			id_range = (152, 251)
		elif generation.value == 3:
			id_range = (252, 386)
		elif generation.value == 4:
			id_range = (387, 493)
		elif generation.value == 5:
			id_range = (494, 649)
		elif generation.value == 6:
			id_range = (650, 721)
		elif generation.value == 7:
			id_range = (722, 809)
		elif generation.value == 8:
			id_range = (810, 905)

		choice = random.randint(*id_range)

		pokemon = self.guesserService.get_pokemon_by_id(choice)

		now = datetime.utcnow()

		guesser = Guesser(
			channel=interaction.channel,
			pokemon=pokemon,
			start_time=now,
			end_time=now + timedelta(seconds=timeout),
		)

		self.guesserService.add_guesser(guesser)

		file = File(pokemon.hidden_img_path, filename='hidden.png')

		embed = guess_view.HiddenEmbed(guesser, file)
		await interaction.response.send_message(embed=embed, file=file)

	@commands.Cog.listener()
	async def on_message(self, message: Message):

		# bot filter
		if message.author.bot == True:
			return

		guesser = self.guesserService.get_guesser(message.channel)
		
		# if none, than there is no guesser for this channel
		if guesser == None:
			return
		
		guesser.total_guesses += 1

		content = message.content.strip().lower()

		# if guess is right
		if content == guesser.pokemon.name.lower():

			guesser.winner = message.author

			await self.guesserService.end_guesser(message.channel)
			return

		# TODO Encourage when a user says they don't know
		# if content == 'idk' or content == 'i don\'t know':
		# 	if random.random() > 0.75:
		# 		await message.channel.send('Keep trying!')

		# TODO Send a hint if the user is requesting it
		# if content == 'give me a hint' or content == 'I need help':
		# 	await message.channel.send('it's from the generation x')
		# 	await message.channel.send('the first letter is x')



	async def on_guess_end(self, guesser: Guesser):

		try:
			file = File(guesser.pokemon.revealed_img_path)
			embed = guess_view.RevealedEmbed(guesser, file)
			await guesser.channel.send(embed=embed, file=file)
		except discord.errors.NotFound:
			log.warn(f'The channel {guesser.channel.id} could not be found')
