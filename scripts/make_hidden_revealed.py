from datetime import datetime
import sys
import os
import logging
from pathlib import Path
from PIL import Image

SOURCE_DIR = Path('./pokemons/originals/')
HIDDEN_DIR = Path('./pokemons/hidden/')
REVEALED_DIR = Path('./pokemons/revealed/')

BACKGROUND_PATH = Path('./resources/background.png')
IMAGE_SIZE = (260, 260)

MAIN_COLOR = (16, 88, 178, 255)
OUTLINE_COLOR = (20, 62, 135, 255)
OUTLINE_OFFSET = (-1, -1)
SHADOW_COLOR = (0, 0, 0, 135)
SHADOW_OFFSET = (-6, 8)



logging.basicConfig(
	stream=sys.stdout,
	level=logging.INFO,
	datefmt='%Y-%m-%d %H:%M:%S',
	format='%(levelname)s [ %(asctime)s ] %(message)s',
)



def create_dirs(directory: Path):

	if not directory.exists():
		logging.info(f'Creating directory {directory}')
		os.makedirs(directory)

	if not directory.is_dir():
		raise Exception(f'{directory} has to be a directory')



def make_silhouette(img: Image.Image, color: tuple[int], offset: tuple[int]) -> Image.Image:
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



def layer_images(imgs: list[Image.Image]) -> Image.Image:
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

def get_process_ids():
	files: list[str] = []
	for file in os.listdir(HIDDEN_DIR):
		files.append(file)

	return [int(file.split("_")[0]) for file in files]

def main():

	start_time = datetime.now()

	create_dirs(HIDDEN_DIR)
	create_dirs(REVEALED_DIR)

	already_process_ids: list[int] = get_process_ids()

	for file in os.listdir(SOURCE_DIR):

		file_id = int(file.split("_")[0])
		if file_id in already_process_ids:
			logging.info(f'{file_id} already processed, skipping')
			continue

		original_path = Path(SOURCE_DIR, file)
		original_img = layer_images([
			Image.new('RGBA', IMAGE_SIZE, (0,0,0,0)),
			Image.open(original_path, 'r'),
		])

		hidden_path = Path(HIDDEN_DIR, file)
		revealed_path = Path(REVEALED_DIR, file)

		logging.info(f'Processing file \'{file}\' {original_img.size}')

		background_img = Image.open(BACKGROUND_PATH).resize(IMAGE_SIZE)

		shadow_img = make_silhouette(original_img, SHADOW_COLOR, SHADOW_OFFSET)

		silhouette_img = layer_images([
			shadow_img,
			make_silhouette(original_img, OUTLINE_COLOR, OUTLINE_OFFSET),
			make_silhouette(original_img, MAIN_COLOR, (0,0)),
		])

		# scale down and up to create some compression/blur effect
		silhouette_img = silhouette_img.resize((150, 150)).resize(silhouette_img.size)

		pokemon_img = layer_images([
			shadow_img,
			original_img,
		])

		# scale down and up to create some compression/blur effect
		pokemon_img = pokemon_img.resize((150, 150)).resize(pokemon_img.size)

		hidden_img = layer_images([
			background_img,
			silhouette_img
		])

		revealed_img = layer_images([
			background_img,
			pokemon_img
		])

		logging.info(f'Saving to {hidden_path}')
		hidden_img.save(hidden_path)
		logging.info(f'Saving to {revealed_path}')
		revealed_img.save(revealed_path)

	logging.info(f'Done, [{datetime.now() - start_time}]')

if __name__ == '__main__':
	main()
