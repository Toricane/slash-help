# SlashHelp
discord-py-interactions v3 slash command help
[Discord server](https://discord.gg/Sk5qDBGPsQ)

## Usage:
```py
from discord_slash import SlashCommand
from discord.ext import commands
from slash_help import SlashHelp

bot = commands.Bot("/")
slash = SlashCommand(bot, sync_commands=True)  # sync_commands=True preferred
slash_help = SlashHelp(bot)
# and its done!
```
## Install:
```
pip install -U slash-help
```

## Arguments:
### Required:
- `bot`: `Union[commands.Bot, discord.Client]` - the bot variable

### Optional:
- `guild_ids`: `Optional[List[int]] = None` - a list of guild/server IDs to register /help
- `color`: `Optional[discord.Color] = discord.Color.default()` - the color of the embed
- `colour` - alias of `color`
- `timeout`: `Optional[int] = 60` - the number of seconds till paginator timeout, specify `None` for no timeout
- `fields_per_embed`: `Optional[int] = 5` - the number of fields per embed
- `extended_buttons`: `Optional[bool] = True` - to use the first and last buttons
- `use_select`: `Optional[bool] = True` - whether or not to use the select
