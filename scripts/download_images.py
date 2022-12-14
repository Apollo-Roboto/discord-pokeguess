from datetime import datetime
import sys
import os
import shutil
import logging
from pathlib import Path
from dataclasses import dataclass
import json
import requests

OUT_DIR = Path('./pokemons/originals/')
POKEDEX = Path('./pokemons/pokedex.json')

logging.basicConfig(
	stream=sys.stdout,
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S',
	format='%(levelname)s [ %(asctime)s ] %(message)s',
)

@dataclass
class Pokemon:
	abilities: list[str]
	detailPageURL: str
	weight: str
	weakness: list[str]
	number: str
	height: int
	collectibles_slug: str
	featured: bool
	slug: str
	name: str
	ThumbnailAltText: str
	ThumbnailImage: str
	id: int
	type: list[str]

	@property
	def file_name(self) -> str:
		return str(self.id) + '_' + self.name.replace(":", "") + '.png'

def get_all_pokemons() -> list[Pokemon]:

	data = {}

	# if the json pokedex exist, use it
	if POKEDEX.exists():
		logging.info('Opening the pokedex')
		with open(POKEDEX, 'r', encoding='utf-8') as f:
			data = json.load(f)

	# else, download the pokedex
	else:

		url = 'https://www.pokemon.com/us/api/pokedex'

		logging.info('Request to ' + url)
		response = requests.get(url)

		response.raise_for_status()

		data = response.json()

		logging.info('Saving the Pokedex')
		with open(POKEDEX, 'w') as f:
			json.dump(data, f)

	return [Pokemon(**entry) for entry in data]

def get_downloaded_ids() -> list[int]:
	"""Look into the out directory for files that was already downloaded"""

	files: list[str] = []
	for file in os.listdir(OUT_DIR):
		files.append(file)

	return [int(file.split("_")[0]) for file in files]

def download_image(pokemon: Pokemon):
	start_time = datetime.now()
	logging.info(f'Starting download of pokemon #{pokemon.id} {pokemon.name}')

	response = requests.get(pokemon.ThumbnailImage, stream=True)

	response.raise_for_status()

	file_path = Path(OUT_DIR, pokemon.file_name)

	with open(file_path, 'wb') as f:
		shutil.copyfileobj(response.raw, f)

	logging.info(f'Download successful [{datetime.now() - start_time}]')

def main() -> None:

	# create directory if it does not exists
	if not OUT_DIR.exists():
		logging.info(f'Creating directory {OUT_DIR}')
		os.makedirs(OUT_DIR)

	# validate the variable to be a directory
	if not OUT_DIR.is_dir():
		raise Exception(f'{OUT_DIR} has to be a directory')

	# get already downloaded images (in case the script failed at any point)
	already_downloaded_ids: list[int] = get_downloaded_ids()

	pokemons = get_all_pokemons()
	logging.info(f'There are {len(pokemons) - len(already_downloaded_ids)} images to download')

	# some pokemons are listed twice, but always following, this last id is to skip duplicates
	last_id = 0

	for pokemon in pokemons:

		if pokemon.id == last_id:
			logging.info('duplicated id, skipping...')
			continue

		# if this image is already downloaded, skip
		if pokemon.id in already_downloaded_ids:
			logging.info(f'Pokemon #{pokemon.id} {pokemon.name} already downloaded')
			continue

		download_image(pokemon)
		last_id = pokemon.id







if __name__ == '__main__':
	main()
