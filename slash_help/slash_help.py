from discord_slash.utils.manage_commands import create_option
from discord_slash import SlashContext, SlashCommand

from discord import Embed, Colour, Color
from discord import Client
from discord.ext.commands import Bot
from discord.ext.commands import GroupMixin

from dinteractions_Paginator import Paginator

from typing import Union, Optional, List
from re import search

from .errors import CommandsNotFound, NameNeeded, IncorrectName


def typer_dict(_type, choices=None) -> str:
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
    return _typer_dict[_type] if choices == [] else "choices"


async def get_all_commands(slash):
    return await slash.to_dict()


async def async_all_commands(self):
    result = await self.slash.to_dict()
    if result["global"]:  # if there are global commands
        return result["global"]
    elif result["guild"] and self.guild_ids is not None:  # if there are guild commands
        guild_has_commands = False
        guild_with_commands = None
        for guild_id in self.guild_ids:
            if result["guild"][guild_id]:
                guild_has_commands = True
                guild_with_commands = guild_id
                break
        if not guild_has_commands:  # no commands in specified guild
            raise CommandsNotFound
        return result["guild"][guild_with_commands]
    else:  # if there are no commands
        raise CommandsNotFound


async def async_separated(self):
    _all_commands = await async_all_commands(self)
    commands = []
    subcommands = []
    for command in _all_commands:
        if command["options"]:
            if command["options"][0]["type"] in (1, 2):
                subcommands.append(command)
                continue
        commands.append(command)
    return [commands, subcommands]


class SlashHelp:
    def __init__(
        self,
        bot: Union[Bot, Client],
        slash: SlashCommand,
        guild_ids: Optional[List[int]] = None,
        *,
        color: Optional[Color] = Color.default(),
        colour: Optional[Colour] = Colour.default(),
        timeout: Optional[int] = 60,
        fields_per_embed: Optional[int] = 4,
        footer: Optional[str] = None,
        front_description: Optional[str] = None,
        no_category_name: Optional[str] = "No Category",
        no_category_description: Optional[str] = "No description",
        extended_buttons: Optional[bool] = True,
        use_select: Optional[bool] = True,
        author_only: Optional[bool] = False,
        use_subcommand: Optional[bool] = False,
        bot_name: Optional[str] = None,
        dpy_command: Optional[bool] = False,
    ) -> None:
        self.bot = bot
        self.slash = slash
        self.guild_ids = guild_ids
        self.colour = (
            colour
            if colour != Colour.default()
            else color
            if color != Color.default()
            else colour
        )
        self.timeout = timeout
        self.fields_per_embed = fields_per_embed
        self.footer = footer
        self.front_description = front_description
        self.no_category_name = no_category_name
        self.no_category_description = no_category_description
        self.extended_buttons = extended_buttons
        self.use_select = use_select
        self.author_only = author_only
        self.use_subcommand = use_subcommand
        self.bot_name = bot_name
        self.dpy_command = dpy_command

        if not self.use_subcommand:
            self.slash.add_slash_command(
                self.send_help,
                "help",
                "Get help!",
                options=[create_option("command", "What command?", 3, False)],
                guild_ids=self.guild_ids,
            )
        else:
            if bot_name is None:
                raise NameNeeded
            is_bot_name = search(r"^[\w-]{1,32}$", bot_name)
            if is_bot_name is None:
                raise IncorrectName
            self.slash.add_subcommand(
                self.send_help,
                base="help",
                name=bot_name,
                description="Get help!",
                options=[create_option("command", "What command?", 3, False)],
                guild_ids=self.guild_ids,
            )
        if self.dpy_command:

            @GroupMixin.command(bot, name="help")
            async def _help(ctx, *, command=None):
                await self.send_help(ctx, command)

    async def send_help(self, ctx: SlashContext, command: Optional[str] = None) -> None:
        commands, subcommands = await async_separated(self)
        if self.dpy_command:
            dpycmds = self.bot.commands
        cogs = {}
        cog_descs = {}
        for command_ in commands:
            the_cog = getattr(self.slash.commands[command_["name"]], "cog", None)
            cog_name = (
                self.no_category_name if the_cog is None else the_cog.qualified_name
            )
            cogs[cog_name] = []
            cog_descs[cog_name] = (
                self.no_category_name if the_cog is None else the_cog.description
            )
        if self.dpy_command:
            for command_ in dpycmds:
                if not command_.hidden:
                    the_cog = command_.cog
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    cogs[cog_name] = []
                    cog_descs[cog_name] = (
                        self.no_category_description
                        if the_cog is None
                        else the_cog.description
                    )
        for command_ in commands:
            the_cog = getattr(self.slash.commands[command_["name"]], "cog", None)
            cog_name = (
                self.no_category_name if the_cog is None else the_cog.qualified_name
            )
            cogs[cog_name].append(
                [command_["name"], command_["description"], command_["options"]]
            )
        if self.dpy_command:
            for command_ in dpycmds:
                if not command_.hidden:
                    the_cog = command_.cog
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    cogs[cog_name].append(
                        [command_.name, command_.description, command_.signature]
                    )
        for subcommand in subcommands:
            base = subcommand["name"]
            sub_command_groups = []
            sub_commands = []
            sub_command_group_name = []
            for option in subcommand["options"]:
                if option["type"] == 1:
                    sub_commands.append(option["name"])
                elif option["type"] == 2:
                    sub_command_groups.append(option["name"])
                    sub_command_group_name.append(option["options"][0]["name"])
            if sub_commands:
                for sub_command in sub_commands:
                    the_cog = getattr(
                        self.slash.subcommands[base][sub_command], "cog", None
                    )
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    if cog_name not in cogs.keys():
                        cogs[cog_name] = []
                        cog_descs[cog_name] = (
                            "No description" if the_cog is None else the_cog.description
                        )
            if sub_command_groups:
                for sub_command_group in sub_command_groups:
                    for sub_command in sub_command_group_name:
                        the_cog = getattr(
                            self.slash.subcommands[base][sub_command_group][
                                sub_command
                            ],
                            "cog",
                            None,
                        )
                        cog_name = (
                            self.no_category_name
                            if the_cog is None
                            else the_cog.qualified_name
                        )
                        if cog_name not in cogs.keys():
                            cogs[cog_name] = []
                            cog_descs[cog_name] = (
                                "No description"
                                if the_cog is None
                                else the_cog.description
                            )
        for subcommand in subcommands:
            base = subcommand["name"]
            sub_command_groups = []
            sub_commands = []
            sub_command_descs = []
            sub_command_opts = []
            sub_command_group_name = []
            sub_command_group_descs = []
            sub_command_group_opts = []
            for option in subcommand["options"]:
                if option["type"] == 1:
                    sub_commands.append(option["name"])
                    sub_command_descs.append(option["description"])
                    sub_command_opts.append(option["options"])
                elif option["type"] == 2:
                    sub_command_groups.append(option["name"])
                    sub_command_group_name.append(option["options"][0]["name"])
                    sub_command_group_descs.append(option["options"][0]["description"])
                    sub_command_group_opts.append(option["options"][0]["options"])
            if sub_commands:
                for sub_command in sub_commands:
                    the_cog = getattr(
                        self.slash.subcommands[base][sub_command], "cog", None
                    )
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    cogs[cog_name].append(
                        [
                            f"{base} {sub_command}",
                            sub_command_descs,
                            sub_command_opts,
                        ]
                    )
            if sub_command_groups:
                for sub_command_group in sub_command_groups:
                    for sub_command in sub_command_group_name:
                        the_cog = getattr(
                            self.slash.subcommands[base][sub_command_group][
                                sub_command
                            ],
                            "cog",
                            None,
                        )
                        cog_name = (
                            self.no_category_name
                            if the_cog is None
                            else the_cog.qualified_name
                        )
                        cogs[cog_name].append(
                            [
                                f"{base} {sub_command_group} {sub_command}",
                                sub_command_group_descs,
                                sub_command_group_opts,
                            ]
                        )
        if self.dpy_command:
            same = {}
            for cmd in self.bot.commands:
                if not cmd.hidden:
                    for cmds in cogs.values():
                        if cmd.name in cmds[0]:
                            same[cmd.name] = {
                                "cmd": cmd,
                                "name": cmd.name,
                                "cog": cmd.cog_name,
                            }
        if command is not None:
            command = command[1:] if command.startswith("/") else command
            matches = []
            matches_desc = []
            matches_opt = []
            matches_cog = []
            matches_embeds = []
            cog_matches = []
            cog_matches_desc = []
            for _cog in cogs.keys():
                if (
                    command.lower() in _cog.lower()
                    and not _cog == self.no_category_name
                ):
                    cog_matches.append(_cog)
                    cog_matches_desc.append(cog_descs[_cog])
                for lst in cogs[_cog]:
                    if command in lst[0]:
                        matches.append(lst[0])
                        matches_desc.append(lst[1])
                        matches_opt.append(lst[2])
                        matches_cog.append(_cog)
            if len(matches) == 0 and len(cog_matches) == 0:
                await ctx.send(
                    "No matches found. Please try searching something different!"
                )
                return
            for i in range(0, (len(matches) + len(cog_matches)), self.fields_per_embed):
                start_at = i - 1
                embed1 = Embed(
                    title=f"Results for `{command}`",
                    description=f"Search results {i + 1} - {i + self.fields_per_embed}",
                    colour=self.colour,
                )
                remainder = i + self.fields_per_embed
                for match in cog_matches[i : (i + self.fields_per_embed)]:
                    value1 = f"Category\n{cog_matches_desc[cog_matches[i : (i + self.fields_per_embed)].index(match, start_at + 1)]}\nCommands:\n"
                    for cmd in cogs[match]:
                        value1 += f"`/{cmd[0]}`, "
                    value1 = value1[:-2] if value1.endswith(", ") else value1
                    embed1.add_field(
                        name=match,
                        value=value1,
                        inline=False,
                    )
                    remainder -= 1
                    start_at = cog_matches[i : (i + self.fields_per_embed)].index(
                        match, start_at + 1
                    )
                start_at = i - 1
                for match in matches[i:remainder]:
                    theres_dpy = ""
                    if self.dpy_command and match in same.keys():
                        theres_dpy = f"You can also use `{self.bot.command_prefix if not isinstance(matches_opt[matches[i:remainder].index(match, start_at + 1)], (str, type(None))) else '/'}{match}`"
                    usage = f"Command\nIn {self.no_category_description if matches_cog[matches[i:remainder].index(match, start_at + 1)] == self.no_category_name else f'In {matches_cog[matches[i:remainder].index(match, start_at + 1)]}'}\n{matches_desc[matches[i:remainder].index(match, start_at + 1)][0] if isinstance(matches_desc[matches[i:remainder].index(match, start_at + 1)], list) else matches_desc[matches[i:remainder].index(match, start_at + 1)] if matches_desc[matches[i:remainder].index(match, start_at + 1)] != '' else 'No Description.'}\n{theres_dpy}\nHow to use:"
                    how_to_use = f"\n```\n{'/' if not isinstance(matches_opt[matches[i:remainder].index(match, start_at + 1)], (str, type(None))) else self.bot.command_prefix}{match} "
                    for _dict in matches_opt[
                        matches[i:remainder].index(match, start_at + 1)
                    ]:
                        if isinstance(_dict, list):
                            for _dict_ in _dict:
                                _type = typer_dict(_dict_["type"], _dict_["choices"])
                                how_to_use += f"[{_dict_['name']}: {'optional ' if not _dict_['required'] else ''}{_type}], "
                        elif isinstance(_dict, dict):
                            _type = typer_dict(_dict["type"], _dict["choices"])
                            how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
                        elif isinstance(_dict, str):
                            how_to_use += _dict
                    how_to_use = (
                        how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                    )
                    how_to_use += "\n```"
                    usage += how_to_use
                    embed1.add_field(name=match, value=usage, inline=False)
                    start_at = matches[i:remainder].index(match, start_at + 1)
                if self.footer is not None:
                    embed1.set_footer(text=self.footer)
                matches_embeds.append(embed1)
            if len(matches_embeds) == 1:
                await ctx.send(embed=matches_embeds[0])
            else:
                await Paginator(
                    self.bot,
                    ctx,
                    matches_embeds,
                    timeout=self.timeout,
                    useFirstLast=self.extended_buttons,
                    useSelect=self.use_select,
                    authorOnly=self.author_only,
                ).run()
        else:
            first_page = (
                Embed(title="Help", color=self.colour)
                if self.front_description is None
                else Embed(
                    title="Help", description=self.front_description, color=self.colour
                )
            )
            for _cog in cogs:
                value1 = f"{self.no_category_description if _cog == 'No Category' else cog_descs[_cog]}\n"
                for cmd in cogs[_cog]:
                    value1 += f"`/{cmd[0]}`, "
                value1 = value1[:-2] if value1.endswith(", ") else value1
                first_page.add_field(name=_cog, value=value1, inline=False)
            if self.footer is not None:
                first_page.set_footer(text=self.footer)
            pages = [first_page]
            for _cog in cogs:
                for i in range(0, len(cogs[_cog]), self.fields_per_embed):
                    embed2 = Embed(
                        title=f"{_cog} {i + 1} - {i + self.fields_per_embed}",
                        description=self.no_category_description
                        if _cog == self.no_category_name
                        else cog_descs[_cog],
                        colour=self.colour,
                    )
                    for cmd in cogs[_cog][i : (i + self.fields_per_embed)]:
                        cmd_name = cmd[0]
                        cmd_desc = cmd[1]
                        cmd_opts = cmd[2]
                        theres_dpy = "\n"
                        if self.dpy_command and cmd_name in same.keys():
                            theres_dpy = (
                                f"\nYou can also use `{self.bot.command_prefix}{cmd_name}`\n"
                                if not isinstance(cmd_opts, (str, type(None)))
                                else f"\nYou can also use `/{cmd_name}`\n"
                            )
                        desc = (
                            (
                                "No description"
                                if (
                                    cmd_desc is None or cmd_desc == [] or cmd_desc == ""
                                )
                                else (
                                    cmd_desc[0]
                                    if isinstance(cmd_desc, list)
                                    else cmd_desc
                                )
                            )
                            + theres_dpy
                            + "How to use:"
                        )
                        how_to_use = f"\n```\n{'/' if not isinstance(cmd_opts, (str, type(None))) else self.bot.command_prefix}{cmd_name} "
                        if not isinstance(cmd_opts, (str, type(None))):
                            for _dict in cmd_opts:
                                if isinstance(_dict, list):
                                    for _dict_ in _dict:
                                        _type = typer_dict(
                                            _dict_["type"], _dict_["choices"]
                                        )
                                        how_to_use += f"[{_dict_['name']}: {'optional ' if not _dict_['required'] else ''}{_type}], "
                                else:
                                    _type = typer_dict(_dict["type"], _dict["choices"])
                                    how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
                        elif cmd_opts is None:
                            pass
                        else:
                            how_to_use += cmd_opts
                        how_to_use = (
                            how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                        )
                        how_to_use += "\n```"
                        embed2.add_field(
                            name=cmd_name, value=desc + how_to_use, inline=False
                        )
                    if self.footer is not None:
                        embed2.set_footer(text=self.footer)
                    pages.append(embed2)
            await Paginator(
                self.bot,
                ctx,
                pages,
                timeout=self.timeout,
                useFirstLast=self.extended_buttons,
                useSelect=self.use_select,
                authorOnly=self.author_only,
            ).run()
