from discord_slash.utils.manage_commands import create_option
from discord_slash import SlashContext

from discord import Embed, Colour
from discord import Client
from discord.ext.commands import Bot

from dinteractions_Paginator import Paginator

from typing import Union, Optional, List

from .errors import NoSlashVar


def typer_dict(_type) -> str:
    _typer_dict = {
        1: "sub_command",
        2: "sub_command_group",
        3: "string",
        4: "integer",
        5: "boolean",
        6: "user",
        7: "channel",
        8: "role",
        9: "mentionable",
        10: "float",
    }
    return _typer_dict[_type]


class SlashHelp:
    def __init__(
        self,
        bot: Union[Bot, Client],
        guild_ids: Optional[List[int]] = None,
        colour: Optional[Colour] = Colour.default(),
        timeout: Optional[int] = 60,
        fields_per_embed: Optional[int] = 5,
        extended_buttons: Optional[bool] = True,
        use_select: Optional[bool] = True,
    ) -> None:
        if not hasattr(bot, "slash"):
            raise NoSlashVar
        self.bot = bot
        self.slash = bot.slash
        self.guild_ids = guild_ids
        self.colour = colour
        self.timeout = timeout
        self.fields_per_embed = fields_per_embed
        self.extended_buttons = extended_buttons
        self.use_select = use_select

        self.slash.add_slash_command(
            self.send_help,
            "help",
            "Get help!",
            options=[create_option("command", "What command?", 3, False)],
            guild_ids=self.guild_ids,
        )

    async def send_help(self, ctx: SlashContext, command: Optional[str] = None) -> None:
        if command is not None:
            return
        commands = self.slash.commands.values()
        subcommands = self.slash.subcommands.values()
        _cmds = []
        _cmdopts = []
        _cmddescs = []
        _subs = []
        _subopts = []
        _subdescs = []
        for sub in subcommands:
            for key in sub.keys():
                try:
                    _subs.append(
                        f"{sub[key].base}{f' {sub[key].subcommand_group} ' if sub[key].subcommand_group is not None else ' '}{key}"
                    )
                    _subopts.append(sub[key].options)
                    _subdescs.append(sub[key].description)
                except AttributeError:
                    subc = sub[key].values()
                    for s in subc:
                        _subs.append(
                            f"{s.base}{f' {s.subcommand_group} ' if s.subcommand_group is not None else ' '}{s.name}"
                        )
                        _subopts.append(s.options)
                        _subdescs.append(s.description)
        x = 0
        for cmd in commands:
            in_sub = False
            if x == 0:
                x += 1
                continue
            for sub in _subs:
                if cmd.name in sub:
                    in_sub = True
            if not in_sub:
                _cmds.append(cmd.name)
                _cmdopts.append(cmd.options)
                _cmddescs.append(cmd.description)
        string = ""
        num_cmds = len(_cmds)
        num_subs = len(_subs)
        pages = []
        embed = Embed(title="Help", colour=self.colour)
        embed.set_footer(text="Type /help command for more info on a command.")
        for cmd in _cmds:
            string += cmd + "\n"
        embed.add_field(name="Commands:", value=string)
        string = ""
        for sub in _subs:
            string += sub + "\n"
        embed.add_field(name="Subcommands:", value=string)
        pages.append(embed)
        for i in range(0, num_cmds, self.fields_per_embed):
            embed2 = Embed(
                title=f"Commands {i + 1} - {i + self.fields_per_embed}",
                description="The commands of the bot!",
                colour=self.colour,
            )
            for cmd in _cmds[i : (i + self.fields_per_embed)]:
                options = _cmdopts[_cmds.index(cmd)]
                desc = (
                    "No description"
                    if _cmddescs[_cmds.index(cmd)] is None
                    else _cmddescs[_cmds.index(cmd)]
                ) + "\nHow to use:"
                how_to_use = f"\n```\n/{cmd} "
                for _dict in options:
                    _type = typer_dict(_dict["type"])
                    how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
                how_to_use = (
                    how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                )
                how_to_use += "\n```"
                embed2.add_field(name=cmd, value=desc + how_to_use, inline=False)
            pages.append(embed2)
        for i in range(0, num_subs, self.fields_per_embed):
            embed3 = Embed(
                title=f"Subcommands {i + 1}-{i + self.fields_per_embed}",
                description="The subcommands of the bot!",
                colour=self.colour,
            )
            for sub in _subs[i : (i + self.fields_per_embed)]:
                options = _subopts[_subs.index(sub)]
                desc = (
                    "No description"
                    if _subdescs[_subs.index(sub)] is None
                    else _subdescs[_subs.index(sub)]
                ) + "\nHow to use:"
                how_to_use = f"\n```\n/{sub} "
                for _dict in options:
                    _type = typer_dict(_dict["type"])
                    how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
                how_to_use = (
                    how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                )
                how_to_use += "\n```"
                embed3.add_field(name=sub, value=desc + how_to_use, inline=False)
            pages.append(embed3)
        await Paginator(
            self.bot,
            ctx,
            pages,
            timeout=self.timeout,
            useFirstLast=self.extended_buttons,
            useSelect=self.use_select,
        ).run()
