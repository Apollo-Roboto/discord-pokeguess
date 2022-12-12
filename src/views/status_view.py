from discord import Embed, Color
from models.status import Status

color = Color.from_str('#5865f2')

class StatusEmbed(Embed):
	def __init__(self, status: Status):
		super().__init__()

		self.color = color
		self.title = 'Current Status'
		self.add_field(name='Ready', value=status.ready, inline=True)
		self.add_field(name='CPU', value=f'{status.cpu}%', inline=True)
		self.add_field(name='RAM', value=f'{status.ram}%', inline=True)
