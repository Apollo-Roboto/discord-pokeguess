
from datetime import datetime
from pathlib import Path
import tempfile
from discord import Attachment
import uuid
import logging
import os
from PIL import Image

log = logging.getLogger(__name__)

# ORIGINAL_DIR = Path('./pokemons', 'originals')
# REVEALED_DIR = Path('./pokemons', 'revealed')
# HIDDEN_DIR = Path('./pokemons', 'hidden')


BACKGROUND_PATH = Path('./resources/background.png')
BACKGROUND_SIZE = (260, 260)
POKEMON_SIZE = (215, 215)
MAIN_COLOR = (16, 88, 178, 255)
OUTLINE_COLOR = (20, 62, 135, 255)
OUTLINE_OFFSET = (-1, -1)
SHADOW_COLOR = (0, 0, 0, 135)
SHADOW_OFFSET = (-6, 8)




class ImageService:
	def __init__(self) -> None:

		# Cached background image
		self._background_image: Image.Image = None



	def make_silhouette(self, img: Image.Image, color: tuple[int], offset: tuple[int]) -> Image.Image:
		silhouette = Image.new(img.mode, img.size, (0,0,0,0))

		for x in range(img.size[0]):

			if (x + offset[0]) >= img.size[0] or (x + offset[0]) < 0: continue

			for y in range(img.size[1]):
				original_pos = (x, y)
				original_pixel = img.getpixel(original_pos)

				silhouette_pos = (x+offset[0], y+offset[1])

				if silhouette_pos[1] >= img.size[1] or silhouette_pos[1] < 0: continue

				opacity = int((color[3]/255) * original_pixel[3])

				new_pixel = (color[0], color[1], color[2], opacity)

				silhouette.putpixel(silhouette_pos, new_pixel)

		return silhouette



	def layer_images(self, imgs: list[Image.Image]) -> Image.Image:
		first = imgs[0]
		mode = first.mode
		size = first.size

		result = Image.new(mode, size, (0, 0, 0, 0))

		center = (int(size[0]/2), int(size[1]/2))

		for img in imgs:

			img_center = (int(img.size[0]/2), int(img.size[1]/2))

			offset = (
				center[0]-img_center[0],
				center[1]-img_center[1]
			)

			result.paste(img, mask=img, box=offset)

		return result

	def get_background_image(self):
		if self._background_image == None:
			self._background_image = Image.open(BACKGROUND_PATH).resize(BACKGROUND_SIZE)

		return self._background_image
	
	def process_image(self, original_path: Path, hidden_path: Path, revealed_path: Path):
		log.info(f'Starting to process {original_path}')

		start_time = datetime.now()

		# Creating output directories
		os.makedirs(hidden_path.parent, exist_ok=True)
		os.makedirs(revealed_path.parent, exist_ok=True)

		# Create original image and scaling the canvas to the background
		original_img = self.layer_images([
			Image.new('RGBA', BACKGROUND_SIZE, (0,0,0,0)),
			Image.open(original_path, 'r').resize(POKEMON_SIZE),
		])

		background_img = self.get_background_image()

		shadow_img = self.make_silhouette(original_img, SHADOW_COLOR, SHADOW_OFFSET)

		silhouette_img = self.layer_images([
			shadow_img,
			self.make_silhouette(original_img, OUTLINE_COLOR, OUTLINE_OFFSET),
			self.make_silhouette(original_img, MAIN_COLOR, (0,0)),
		])

		# scale down and up to create some compression/blur effect
		silhouette_img = silhouette_img.resize((150, 150)).resize(silhouette_img.size)

		pokemon_img = self.layer_images([
			shadow_img,
			original_img,
		])

		pokemon_img = pokemon_img.resize((150, 150)).resize(pokemon_img.size)

		hidden_img = self.layer_images([
			background_img,
			silhouette_img,
		])

		revealed_img = self.layer_images([
			background_img,
			pokemon_img,
		])

		logging.info(f'Saving {hidden_path}')
		hidden_img.save(hidden_path)
		logging.info(f'Saving {revealed_path}')
		revealed_img.save(revealed_path)

		log.info(f'Done [{datetime.now() - start_time}]')