import os
from pathlib import Path
import logging
import re
from typing import Union, Callable, Awaitable
from datetime import datetime
from discord import TextChannel
from discord.ext import tasks
from models.pokemon import Pokemon
from models.guesser import Guesser

log = logging.getLogger(__name__)

HIDDEN_IMG_DIR = Path('./pokemons/hidden/')
REVEALED_IMG_DIR = Path('./pokemons/revealed/')



class GuesserServiceException(Exception): pass
class GuesserAlreadyActiveException(GuesserServiceException): pass



class GuesserService:

	def __init__(self) -> None:

		# Guesser by channel_id
		self.active_guess: dict[int, Guesser] = {}

		self.on_guesser_end_event: list[Callable[[Guesser], Awaitable[None]]] = []

		# pylint: disable=no-member
		self.end_guesses_loop.start()
		# pylint: enable=no-member


	def get_pokemon_by_id(self, pokemon_id):
		log.info(f'Searching for pokemon #{pokemon_id} in the file system')

		for file in os.listdir(HIDDEN_IMG_DIR):
			splitted_name = re.split(r'[_.]', file)

			if pokemon_id == int(splitted_name[0]):

				return Pokemon(
					id=pokemon_id,
					name=splitted_name[1],
					hidden_img_path=Path(HIDDEN_IMG_DIR, file),
					revealed_img_path=Path(REVEALED_IMG_DIR, file),
					original_img_path=None, # Hiding it
				)

		log.error(f'Pokemon #{pokemon_id} not found')

		return None

	def add_guesser(self, guesser: Guesser) -> None:
		if guesser.channel.id in self.active_guess:
			raise GuesserAlreadyActiveException()

		log.info(f'Creating a guesser for pokemon #{guesser.pokemon.id} in channel {guesser.channel.id}')

		self.active_guess[guesser.channel.id] = guesser

	async def end_guesser(self, channel: TextChannel):
		if channel.id not in self.active_guess:
			raise GuesserServiceException()

		guesser = self.active_guess.pop(channel.id)

		log.info(f'Ending guesser for pokemon #{guesser.pokemon.id} in channel {channel.id}')

		for event in self.on_guesser_end_event:
			await event(guesser)

	def get_guesser(self, channel: Union[TextChannel, int]) -> Guesser:

		if isinstance(channel, int):
			return self.active_guess.get(channel, None)
		
		return self.active_guess.get(channel.id, None)

	@tasks.loop(seconds=1)
	async def end_guesses_loop(self):
		channels = list(self.active_guess.keys())

		for channel_id in channels:
			guesser = self.get_guesser(channel_id)

			if guesser.end_time < datetime.utcnow():

				await self.end_guesser(guesser.channel)
