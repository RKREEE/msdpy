import discord
from discord.ext import commands

import json
from random import randint, choice
import time
import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import bot


class General(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# sky server, sky
		self.findseed_whitelist = [672045035797348352, 329538915805691905]

	@commands.command(description='Shows the bot’s ping to Discord')
	async def ping(self, ctx):
		embed = discord.Embed(
			colour=discord.Colour(0xc500ff)
		)

		embed.add_field(
			name="Ping",
			value=f"{round(self.bot.latency * 1000)}ms",
			inline=True
		)

		await ctx.send(embed=embed)

	@commands.command(aliases=['max', 'botinfo', 'bot'])
	async def info(self, ctx):
		version = self.bot.config['version']

		embed = discord.Embed(
			title="Information about this bot",
			colour=discord.Colour(0xc500ff),
			description="This bot was made by Skye. The full source code can be found at https://github.com/Skycloudd/msdpy. The bot is currently hosted by AnInternetTroll."
		)

		embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png"))

		embed.add_field(
			name="Info",
			value=f"ID: {self.bot.user.id}\nName: {self.bot.user.name}\nVersion: {version}",
			inline=True
		)
		embed.add_field(
			name="Ping to the Discord API",
			value=f'{round(self.bot.latency * 1000)}ms',
			inline=True
		)
		embed.add_field(
			name="Library",
			value=f"Discord.py v{discord.__version__}",
			inline=True
		)

		await ctx.send(embed=embed)

	@commands.command(description='Shows how long the bot has been online for')
	async def uptime(self, ctx):
		seconds = time.time() - self.bot.start_time
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)
		w, d = divmod(d, 7)

		embed = discord.Embed(
			colour=discord.Colour(0xc500ff)
		)

		embed.add_field(
			name="Uptime",
			value=f"{int(w)}w : {int(d)}d : {int(h)}h : {int(m)}m : {int(s)}s",
			inline=True
		)

		await ctx.send(embed=embed)

	@commands.command(aliases=['profile'])
	async def userinfo(self, ctx, user: discord.Member=None):
		if not user:
			user = ctx.message.author

		output = ""
		for i in user.roles:
			output += i.mention + " "

		if user.color.value == 0:
			color = 16777210
		else:
			color = user.color

		embed=discord.Embed(title=user.name, description=user.mention, color=color, timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=user.avatar_url_as(format="png"))
		embed.add_field(name="Nickname", value=user.display_name, inline=False)
		embed.add_field(name="Joined on", value=user.joined_at.date(), inline=True)
		embed.add_field(name="Status", value=user.status, inline=True)
		embed.add_field(name="Created account on", value=user.created_at.date(), inline=True)
		embed.add_field(name="Roles", value=output, inline=True)
		embed.set_footer(text=f"ID: {user.id}")
		await ctx.send(embed=embed)

	@commands.command()
	async def serverinfo(self, ctx, guild=None):
		if not guild:
			guild = ctx.message.guild
		else:
			print(type(guild))
			guild = self.bot.get_guild(int(guild))

		if guild.owner.color.value == 0:
			color = 16777210
		else:
			color = guild.owner.color

		emojiList = " "
		for i in guild.emojis:
			emojiList += str(i) + " "

		embed=discord.Embed(title=guild.name, description=guild.description, color=color, timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=guild.icon_url_as(format="png"))
		embed.set_image(url=guild.splash_url_as(format="png"))
		embed.add_field(name="Created on", value=guild.created_at.date(), inline=True)
		embed.add_field(name="Members", value=guild.member_count, inline=True)
		#embed.add_field(name="Emojis", value=emojiList, inline=True)
		embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
		embed.set_footer(text=f"ID: {guild.id}")
		await ctx.send(embed=embed)

	@commands.command(aliases=['commands', 'allcommands'])
	async def listcommands(self, ctx):
		with open('custom_commands.json', 'r') as f:
			commands = json.load(f)
			output = '```List of custom commands:\n'
			for key in commands:
				output += f'{key}, '
			output += '```'
			await ctx.send(output)

	@commands.command()
	async def prefix(self, ctx):
		prefixes = bot.get_prefix(self.bot, ctx.message)
		prefixes.pop(0)
		output = ", ".join(prefixes)

		await ctx.send(f"My prefixes are {output}")

	@commands.command()
	@commands.cooldown(1, 20, commands.BucketType.user)
	async def roll(self, ctx, pool):
		embed = discord.Embed(
			colour=discord.Colour(0xc500ff)
		)

		embed.add_field(
			name="You rolled",
			value=f"{randint(0, int(pool))}",
			inline=True
		)

		await ctx.send(embed=embed)

	@roll.error
	async def roll_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"{ctx.author.mention}, you have to wait {round(error.retry_after, 3)} seconds before using this again")

	@commands.command()
	async def emotes(self, ctx):
		emotes = []
		for emote in self.bot.emojis:
			if emote.available:
				emotes.append(str(emote))

		text = ''
		for i in range(len(emotes)):
			if len(text) + len(str(emotes[i])) > 2000:
				await ctx.send(text)
				text = ''
			text += str(emotes[i])
		await ctx.send(text)

	@commands.command(aliases=['nasa', 'apod'])
	async def nasapic(self, ctx):
		apikey = self.bot.config['nasa_apikey']
		url = f'https://api.nasa.gov/planetary/apod?api_key={apikey}'

		async with self.bot.session.get(url) as r:
			response = json.loads(await r.text())

			embed = discord.Embed(
				title=response["title"],
				colour=discord.Colour(discord.colour.Colour.orange().value),
				url=response["hdurl"],
				description=response["explanation"]
			)

			embed.set_image(url=response["hdurl"])
			embed.set_footer(text=f'copyright: {response["copyright"]}')

			await ctx.send(embed=embed)

	@commands.cooldown(1, 20, commands.BucketType.user)
	@commands.command()
	async def findseed(self, ctx):
		total_eyes = sum([1 for i in range(12) if randint(1,10) == 1])

		# rigged findseed
		if ctx.author.id == 738279874749530172:  # Grape
			total_eyes = 12
		if ctx.author.id == 329538915805691905:  # Skye
			total_eyes += 3
			if total_eyes > 12:
				total_eyes = 12
		if ctx.author.id == 554768592441442315:  # Stephen
			total_eyes = 69

		embed = discord.Embed(
			colour=discord.Colour(0xc500ff)
		)

		embed.add_field(
			name="Findseed",
			value=f"{str(ctx.message.author.mention)} -> your seed is a {total_eyes} eye",
			inline=True
		)

		try:
			await ctx.send(embed=embed)
		except discord.Forbidden:
			await ctx.message.add_reaction('👁️')

	# https://gist.github.com/CapClumsy/6128d89a1e842b4e802b3a077d7f98a5
	@findseed.after_invoke
	async def reset_cooldown(self, ctx):
		for e in self.findseed_whitelist:
			# to whitelist a person:
			if e == ctx.author.id:
				self.findseed.reset_cooldown(ctx)

			# to whitelist a channel:
			if e == ctx.message.channel.id:
				self.findseed.reset_cooldown(ctx)

			# to whitelist a guild/server:
			if e == ctx.message.guild.id:
				self.findseed.reset_cooldown(ctx)

			# to whitelist a role:
			if e in [role.id for role in ctx.author.roles]:
				self.findseed.reset_cooldown(ctx)

	@findseed.error
	async def findseed_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(
				f'{ctx.author.mention}, you have to wait {round(error.retry_after, 3)} seconds before using this again')

	#this command is dumb and i shouldnt have added it
	@commands.is_owner()
	@commands.command(hidden=True)
	async def someone(self, ctx):
		await ctx.send(choice(ctx.guild.members).mention)
					 
					 
	@commands.command(aliases=["vfindseed", "visualfindseed", "vfs"])
async def findseedbutvisual(self, ctx):
        """Test your luck in Minecraft but visual."""
        ignore_cooldown = [745481731133669476, 747984453585993808]
        if ctx.guild.id in ignore_cooldown:
            ctx.command.reset_cooldown(ctx)

        rows = {
            0: [0, 0, 0],
            1: [0, 0, 0],
            2: [0, 0, 0],
            3: [0, 0, 0],
        }
        emojis = [
            "<:empty:755432610984886332>",
            "<:portal:755432641335001238>",
            "<:eyess:755432579905093683>",
        ]
        portalframe = ""
        for r in range(4):
            for e in range(3):
                randomness = randint(1, 10)
                if randomness <= 1:
                    rows[r][e] = 1
        for i in range(4):
            if i == 0 or i == 3:
                portalframe += f" \{rows[i][0]}\{rows[i][1]}\{rows[i][2]}\n"
            else:
                if i == 2:
                    pass
                else:
                    for e in range(3):
                        portalframe += f"\{rows[i][e]}   \{rows[i+1][e]}\n"
        portalframe = portalframe.replace(" ", emojis[0])
        portalframe = portalframe.replace(r"\0", emojis[1])
        portalframe = portalframe.replace(r"\1", emojis[2])
        # print(portalframe)
        e = discord.Embed(
            title="findseed but visual",
            description=f"Your seed looks like: \n\n{portalframe}",
            color=discord.Colour(440052),
        )
        e.set_author(
            name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=ctx.message.author.avatar_url,
        )
        await ctx.send(embed=e)
        # await ctx.send(
        #     f"{ctx.message.author.mention} -> your seed is a {totalEyes} eye"
        # )

	@commands.Cog.listener()
	async def on_message(self, msg):
		if msg.author.bot or not msg.guild or msg.author.id in self.bot.config['blacklist']:
			return
		if "i-" in msg.content.lower():
			try:
				await msg.channel.send(self.bot.get_user(329538915805691905).mention)
			except discord.Forbidden:
				try:
					await msg.add_reaction('😐')
				except discord.Forbidden:
					pass
		if "pog" in msg.content.lower():
			pog_emote = await msg.guild.fetch_emoji(int(self.bot.config[str(msg.guild.id)]["pog_emote_id"]))
			await msg.add_reaction(pog_emote)


def setup(bot):
	bot.add_cog(General(bot))
