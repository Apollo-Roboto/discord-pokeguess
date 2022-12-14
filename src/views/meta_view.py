from discord import Embed, Color, Member, ButtonStyle
import discord

color = Color.from_str('#2f3136')

class InviteEmbed(Embed):
	def __init__(self, bot: Member):
		super().__init__()

		self.color = color
		self.title = 'Invite PokeGuess to your servers!'

		self.set_thumbnail(url=bot.display_avatar.url)



class InviteView(discord.ui.View):
	def __init__(self, bot: Member):
		super().__init__()

		self.add_item(discord.ui.Button(
			label='👀 Click here to invite me to your server!',
			style=ButtonStyle.url,
			url='https://discord.com/api/oauth2/authorize?client_id=1052405591680757961&permissions=2147518464&scope=bot'
		))
