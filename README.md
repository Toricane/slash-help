# slash-help

[![Downloads](https://static.pepy.tech/personalized-badge/slash-help?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pypi.org/project/slash-help/) [![Discord](https://img.shields.io/discord/890021073465270312?color=blue&label=Discord)](https://discord.gg/Sk5qDBGPsQ)

<img src="https://cdn.discordapp.com/attachments/890021074337660959/892945393988554782/new-slash-help-gif.gif" alt="slash-help gif"></img>

discord-py-interactions slash command help

Join our [Discord server](https://discord.gg/Sk5qDBGPsQ) to ask questions, report bugs, or suggest features!

## Install:
```shell
pip install -U slash-help
```
Requirements (automatically installed when installing slash-help):
- discord-py-interactions (version 3.0.2)
- discord.py (version 1.7.3)
- dinteractions-Paginator
- thefuzz
- Levenshtein

## Example:

<img src="https://cdn.discordapp.com/attachments/901252023444467733/901252684114440212/mXxyqtOngt.gif"></img>

## Usage:
```py
from discord_slash import SlashCommand
from discord.ext import commands
from slash_help import SlashHelp

bot = commands.Bot("your_prefix", help_command=None)
slash = SlashCommand(bot, sync_commands=True)  # sync_commands=True preferred
help_slash = SlashHelp(bot, slash, "your_bot_token", dpy_command=True)  # if you want a dpy command as well, and to show dpy commands in the help
# and its done!
```

## More customized:
```py
from discord_slash import SlashCommand
from discord.ext import commands
from slash_help import SlashHelp

bot = commands.Bot("your_prefix", help_command=None)
slash = SlashCommand(bot, sync_commands=True)  # sync_commands=True preferred
help_slash = SlashHelp(bot, slash, "your_bot_token", dpy_command=True, auto_create=False)


@bot.command()
async def help(ctx, *, command=None):
    await help_slash.send_help(ctx, command, prefix="your_prefix")  # you can override the prefix here
                                                                    # and also in SlashHelp()

@slash.slash(name="help")
async def _help(ctx, command=None):
    await help_slash.send_help(ctx, command, guild_id=ctx.guild.id)
```

## *class* SlashHelp
### Arguments:
#### Required:
- `bot`: `Union[commands.Bot, discord.Client]` - the bot variable
- `slash`: `SlashCommand` - the slash variable
- `token`: `str` - the bot token, required for fetching slash commands from Discord API

#### Optional:
- `guild_ids`: `Optional[List[int]] = None` - a list of guild/server IDs to register the help slash command
- `guild_id`: `Optional[int] = None` - what guild ID to use for getting guild commands

##### Keyword Arguments:
- `color`: `Optional[discord.Color] = discord.Color.default()` - the color of the embed
- `colour` - alias of `color`
- `timeout`: `Optional[int] = 60` - the number of seconds till paginator timeout, specify `None` for no timeout
- `fields_per_embed`: `Optional[int] = 4` - the number of fields per embed
- `footer`: `Optional[str] = None` - footer for the embeds
- `front_description`: `Optional[str] = None` - description in the first embed
- `no_category_name`: `Optional[str] = "No Category"` - value for the No Category field
- `no_category_description`: `Optional[str] = "No description"` - value for the No Category description field
- `extended_buttons`: `Optional[bool] = True` - to use the first and last buttons
- `use_select`: `Optional[bool] = True` - whether to use the select
- `author_only`: `Optional[bool] = False` - whether to have buttons work only for the author
- `use_subcommand`: `Optional[bool] = False` - to have a subcommand `/help bot_name`
- `bot_name`: `Optional[str] = None` - needed to use `use_subcommand`
- `dpy_command`: `Optional[bool] = False` - whether to make a discord.py command as well
- `max_search_results`: `Optional[int] = 12` - maximum search results
- `sync_commands`: `Optional[bool] = False` - if you want to get commands every single time
- `blacklist`: `Optional[List[str]] = None` - commands or cogs to blacklist, case sensitive
- `prefix`: `Optional[str] = None` - overrides `bot.command_prefix`
