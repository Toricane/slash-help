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
        no_category_description: Optional[str] = "No description",
        extended_buttons: Optional[bool] = True,
        use_select: Optional[bool] = True,
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
        self.no_category_description = no_category_description
        self.extended_buttons = extended_buttons
        self.use_select = use_select
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
        cogs = {}
        cog_descs = {}
        for command_ in commands:
            the_cog = getattr(self.slash.commands[command_["name"]], "cog", None)
            cog_name = "No Category" if the_cog is None else the_cog.qualified_name
            cogs[cog_name] = []
            cog_descs[cog_name] = (
                "No description" if the_cog is None else the_cog.description
            )
        for command_ in commands:
            the_cog = getattr(self.slash.commands[command_["name"]], "cog", None)
            cog_name = "No Category" if the_cog is None else the_cog.qualified_name
            cogs[cog_name].append(
                [command_["name"], command_["description"], command_["options"]]
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
                        "No Category" if the_cog is None else the_cog.qualified_name
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
                            "No Category" if the_cog is None else the_cog.qualified_name
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
                        "No Category" if the_cog is None else the_cog.qualified_name
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
                            "No Category" if the_cog is None else the_cog.qualified_name
                        )
                        cogs[cog_name].append(
                            [
                                f"{base} {sub_command_group} {sub_command}",
                                sub_command_group_descs,
                                sub_command_group_opts,
                            ]
                        )
        if command is not None:
            matches = []
            matches_desc = []
            matches_opt = []
            matches_cog = []
            matches_embeds = []
            cog_matches = []
            cog_matches_desc = []
            for _cog in cogs.keys():
                if command.lower() in _cog.lower() and not _cog == "No Category":
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
                embed1 = Embed(
                    title=f"Results for `{command}`",
                    description=f"Search results {i + 1} - {i + self.fields_per_embed}",
                    colour=self.colour,
                )
                remainder = i + self.fields_per_embed
                for match in cog_matches[i : (i + self.fields_per_embed)]:
                    value1 = f"Category\n{cog_matches_desc[cog_matches.index(match)]}\nCommands:\n"
                    for cmd in cogs[match]:
                        value1 += f"`/{cmd[0]}`, "
                    value1 = value1[:-2] if value1.endswith(", ") else value1
                    embed1.add_field(
                        name=match,
                        value=value1,
                        inline=False,
                    )
                    remainder -= 1
                for match in matches[i:remainder]:
                    usage = f"Command\n{self.no_category_description if matches_cog[matches.index(match)] == 'No Category' else f'In {matches_cog[matches.index(match)]}'}\n{matches_desc[matches.index(match)][0] if isinstance(matches_desc[matches.index(match)], list) else matches_desc[matches.index(match)]}\nHow to use:"
                    how_to_use = f"\n```\n/{match} "
                    for _dict in matches_opt[matches.index(match)]:
                        if isinstance(_dict, list):
                            for _dict_ in _dict:
                                _type = typer_dict(_dict_["type"])
                                how_to_use += f"[{_dict_['name']}: {'optional ' if not _dict_['required'] else ''}{_type}], "
                        else:
                            _type = typer_dict(_dict["type"], _dict["choices"])
                            how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
                    how_to_use = (
                        how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                    )
                    how_to_use += "\n```"
                    usage += how_to_use
                    embed1.add_field(name=match, value=usage, inline=False)
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
                        if _cog == "No Category"
                        else cog_descs[_cog],
                        colour=self.colour,
                    )
                    for cmd in cogs[_cog][i : (i + self.fields_per_embed)]:
                        cmd_name = cmd[0]
                        cmd_desc = cmd[1]
                        cmd_opts = cmd[2]
                        desc = (
                            "No description"
                            if (cmd_desc is None or cmd_desc == [])
                            else (
                                cmd_desc[0] if isinstance(cmd_desc, list) else cmd_desc
                            )
                        ) + "\nHow to use:"
                        how_to_use = f"\n```\n/{cmd_name} "
                        for _dict in cmd_opts:
                            if isinstance(_dict, list):
                                for _dict_ in _dict:
                                    _type = typer_dict(_dict_["type"])
                                    how_to_use += f"[{_dict_['name']}: {'optional ' if not _dict_['required'] else ''}{_type}], "
                            else:
                                _type = typer_dict(_dict["type"])
                                how_to_use += f"[{_dict['name']}: {'optional ' if not _dict['required'] else ''}{_type}], "
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
            ).run()
