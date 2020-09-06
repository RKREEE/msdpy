# https://gist.github.com/nitros12/2c3c265813121492655bc95aa54da6b9

import ast
import discord

from discord.ext import commands


def insert_returns(body):
	# insert return stmt if the last expression is a expression statement
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])

	# for if statements, we insert returns into the body and the orelse
	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)

	# for with blocks, again we insert returns into the body
	if isinstance(body[-1], ast.With):
		insert_returns(body[-1].body)


class Eval(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.is_owner()
	@commands.command(name='eval')
	async def eval_fn(self, ctx, send_result='false', *, cmd):
		"""Evaluates input.

		Input is interpreted as newline seperated statements.
		If the last statement is an expression, that is the return value.

		Usable globals:
		- `bot`: the bot instance
		- `discord`: the discord module
		- `commands`: the discord.ext.commands module
		- `ctx`: the invokation context
		- `__import__`: the builtin `__import__` function

		Such that `>eval 1 + 1` gives `2` as the result.

		The following invokation will cause the bot to send the text '9'
		to the channel of invokation and return '3' as the result of evaluating

		>eval ```
		a = 1 + 2
		b = a * 2
		await ctx.send(a + b)
		a
		```
		"""
		fn_name = "_eval_expr"

		cmd = cmd.strip("` ")

		# add a layer of indentation
		cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

		# wrap in async def body
		body = f"async def {fn_name}():\n{cmd}"

		parsed = ast.parse(body)
		body = parsed.body[0].body

		insert_returns(body)

		env = {
			'bot': ctx.bot,
			'discord': discord,
			'commands': commands,
			'ctx': ctx,
			'__import__': __import__
		}
		exec(compile(parsed, filename="<ast>", mode="exec"), env)

		result = (await eval(f"{fn_name}()", env))
		if send_result == 'true':
			await ctx.send(f'**result**\n{result}')


def setup(bot):
	bot.add_cog(Eval(bot))
