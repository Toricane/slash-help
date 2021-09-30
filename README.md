# slash-help

<img src="https://cdn.discordapp.com/attachments/890021074337660959/892945393988554782/new-slash-help-gif.gif" alt="slash-help gif"></img>

discord-interactions slash command help

Join our [Discord server](https://discord.gg/Sk5qDBGPsQ) to ask questions, report bugs, or suggest features!

## Example:

<img src="https://cdn.discordapp.com/attachments/890021074337660959/892595756907786270/B9fVWuVhSe.gif"></img>

## Usage:
```py
from discord_slash import SlashCommand
from discord.ext import commands
from slash_help import SlashHelp

bot = commands.Bot("/")
slash = SlashCommand(bot, sync_commands=True)  # sync_commands=True preferred
slash_help = SlashHelp(bot, slash)
# and its done!
```
## Install:
```bash
pip install -U slash-help
```

## *class* SlashHelp
### Arguments:
#### Required:
- `bot`: `Union[commands.Bot, discord.Client]` - the bot variable
- `slash`: `SlashCommand` - the slash variable

#### Optional:
- `guild_ids`: `Optional[List[int]] = None` - a list of guild/server IDs to register /help

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
