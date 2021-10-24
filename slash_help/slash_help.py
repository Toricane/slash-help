from typing import Union, Optional, List
from re import search

from .errors import CommandsNotFound, NameNeeded, IncorrectName

from discord_slash.utils.manage_commands import create_option, get_all_commands
from discord_slash import SlashContext, SlashCommand

from discord import Embed, Colour, Color
from discord import Client
from discord.ext.commands import Bot
from discord.ext.commands import GroupMixin

from dinteractions_Paginator import Paginator
from thefuzz.fuzz import ratio


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
    return _typer_dict[_type] if choices == [] or choices is None else "choices"


class SlashHelp:
    __slots__ = (
        "bot",
        "slash",
        "token",
        "guild_ids",
        "guild_id",
        "colour",
        "timeout",
        "fields_per_embed",
        "footer",
        "front_description",
        "no_category_name",
        "no_category_description",
        "extended_buttons",
        "use_select",
        "author_only",
        "dpy_command",
        "max_search_results",
        "sync_commands",
        "blacklist",
        "prefix",
        "data",
    )

    def __init__(
        self,
        bot: Union[Bot, Client],
        slash: SlashCommand,
        token: str,
        guild_ids: Optional[List[int]] = None,
        guild_id: Optional[int] = None,
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
        max_search_results: Optional[int] = 12,
        sync_commands: Optional[bool] = False,
        blacklist: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        auto_create: Optional[bool] = True,
    ) -> None:
        self.bot = bot
        self.slash = slash
        self.token = token
        self.guild_ids = guild_ids
        self.guild_id = guild_id
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
        self.dpy_command = dpy_command
        self.max_search_results = max_search_results
        self.sync_commands = sync_commands
        self.blacklist = blacklist
        self.prefix = prefix

        self.data = None

        if not use_subcommand and auto_create:
            self.slash.add_slash_command(
                self.send_help,
                "help",
                "Get help!",
                options=[create_option("command", "What command?", 3, False)],
                guild_ids=self.guild_ids,
            )
        else:
            if auto_create:
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
        if self.dpy_command and auto_create:

            @GroupMixin.command(bot, name="help")
            async def _help(ctx, *, command=None):
                await self.send_help(ctx, command)

    async def send_help(
        self,
        ctx: SlashContext,
        command: Optional[str] = None,
        prefix: Optional[str] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        if prefix is not None:
            self.prefix = prefix
        if guild_id is None:
            guild_id = (
                self.guild_id
                if self.guild_id is not None
                else self.guild_ids[0]
                if self.guild_ids is not None
                else guild_id
            )
        duplicates = {}
        if self.data is None or self.sync_commands:
            self.data = await self.async_separated(guild_id)
            if self.dpy_command:
                dpycmds = self.bot.commands
                for dcmd in dpycmds:
                    if not dcmd.hidden:
                        for interaction in self.data:
                            in_blacklist = False
                            if self.blacklist:
                                for black in self.blacklist:
                                    if black in interaction["name"]:
                                        in_blacklist = True
                                        break
                            if in_blacklist:
                                continue
                            if dcmd.name == interaction["name"]:
                                duplicates[dcmd.name] = {
                                    "cmd": dcmd,
                                    "name": dcmd.name,
                                    "cog": dcmd.qualified_name,
                                }
                        self.data.append(
                            {
                                "name": dcmd.name,
                                "description": dcmd.description,
                                "options": dcmd.signature,
                                "type": "message command",
                                "cog": {
                                    "name": self.no_category_name
                                    if dcmd.cog is None
                                    else dcmd.cog.qualified_name,
                                    "description": self.no_category_description
                                    if dcmd.cog is None
                                    else dcmd.cog.description,
                                },
                            }
                        )
        data = self.data.copy()
        if command:
            command = command.lower()
            answers = {}
            list_cogs = []
            list_commands = []
            for interaction in data:
                in_blacklist = False
                if self.blacklist:
                    for black in self.blacklist:
                        if (
                            black in interaction["name"]
                            or black in interaction["cog"]["name"]
                        ):
                            in_blacklist = True
                            break
                if in_blacklist:
                    continue
                percent = ratio(command, interaction["cog"]["name"])
                if interaction["cog"]["name"] not in answers.keys():
                    answers[interaction["cog"]["name"]] = percent
                    list_cogs.append(interaction["cog"]["name"])
            for interaction in data:
                in_blacklist = False
                if self.blacklist:
                    for black in self.blacklist:
                        if (
                            black in interaction["name"]
                            or black in interaction["cog"]["name"]
                        ):
                            in_blacklist = True
                            break
                if in_blacklist:
                    continue
                percent = ratio(command, interaction["name"])
                if interaction["name"] not in answers.keys():
                    answers[interaction["name"]] = percent
                    list_commands.append(interaction["name"])
            sorted_data = sorted(answers, key=answers.get, reverse=True)[
                : self.max_search_results
            ]
            embeds = []
            for i in range(0, (len(sorted_data)), self.fields_per_embed):
                page = Embed(
                    title=f"Results for `{command}` {i + 1} - {i + self.fields_per_embed}",
                    colour=self.colour,
                )

                for match in sorted_data[i : (i + self.fields_per_embed)]:
                    if match in list_cogs:
                        cog = None
                        cmds = []
                        for interaction in data:
                            if match == interaction["cog"]["name"]:
                                cog = interaction["cog"]
                                cmds.append({interaction["name"]: interaction})
                        if cog is not None:
                            value = f"Category\n{self.no_category_description if cog['description'] is None else cog['description']}\nCommands:\n"
                            for cmd in cmds:
                                in_blacklist = False
                                if self.blacklist:
                                    for black in self.blacklist:
                                        if black in list(cmd.keys())[0]:
                                            in_blacklist = True
                                            break
                                if in_blacklist:
                                    continue
                                value += f"`{'/' if list(cmd.values())[0]['type'] in ['slash command', 'subcommand', 'subcommand group',] else '' if 'menu' in list(cmd.values())[0]['type'] else (self.bot.command_prefix if self.prefix is None else self.prefix)}{list(cmd.keys())[0]}`, "
                            value = value[:-2] if value.endswith(", ") else value
                            page.add_field(
                                name=match,
                                value=value,
                                inline=False,
                            )
                    elif match in list_commands:
                        for interaction in data:
                            if match == interaction["name"]:
                                break
                        options = ""
                        if interaction["type"] in [
                            "slash command",
                            "subcommand",
                            "subcommand group",
                        ]:
                            for option in interaction["options"]:
                                the_type = typer_dict(
                                    option["type"],
                                    option["choices"]
                                    if "choices" in option.keys()
                                    else [],
                                )
                                options += f"[{'optional ' if not option['required'] else ''}{the_type}], "
                        elif "menu" in interaction["type"]:
                            pass
                        else:
                            options += interaction["options"]
                        options = options[:-2] if options.endswith(", ") else options
                        how_to_use = f"How to use:\n```\n{'/' if interaction['type'] in ['slash command', 'subcommand', 'subcommand group',] else ('Right click on a ' + interaction['type'].replace(' menu', '')) if 'menu' in interaction['type'] else (self.bot.command_prefix if self.prefix is None else self.prefix)}{'' if 'menu' in interaction['type'] else interaction['name']} {options}\n```"
                        theres_dpy = "\n"
                        if (
                            self.dpy_command
                            and interaction["name"] in duplicates.keys()
                        ):
                            theres_dpy = (
                                f"\nYou can also use `{(self.bot.command_prefix if self.prefix is None else self.prefix)}{interaction['name']}`\n"
                                if not isinstance(
                                    interaction["options"], (str, type(None))
                                )
                                else f"\nYou can also use `/{interaction['name']}`\n"
                            )
                        page.add_field(
                            name=interaction["name"],
                            value=(
                                (
                                    self.no_category_description
                                    if interaction["description"] == ""
                                    else interaction["description"]
                                )
                                + f"\n{interaction['type'].capitalize()}"
                                + theres_dpy
                                + how_to_use
                            ),
                            inline=False,
                        )
                if self.footer is not None:
                    page.set_footer(text=self.footer)
                embeds.append(page)
            await Paginator(
                self.bot,
                ctx,
                embeds,
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
            embeds = [first_page]
            cogs = []
            for interaction in data:
                in_blacklist = False
                if self.blacklist:
                    for black in self.blacklist:
                        if (
                            black in interaction["name"]
                            or black in interaction["cog"]["name"]
                        ):
                            in_blacklist = True
                            break
                if in_blacklist:
                    continue
                if {
                    "name": interaction["cog"]["name"],
                    "description": interaction["cog"]["description"],
                    "interactions": [],
                } not in cogs:
                    cogs.append(
                        {
                            "name": interaction["cog"]["name"],
                            "description": interaction["cog"]["description"],
                            "interactions": [],
                        }
                    )
            for cog in cogs:
                in_blacklist = False
                if self.blacklist:
                    for black in self.blacklist:
                        if black in cog["name"]:
                            in_blacklist = True
                            break
                if in_blacklist:
                    continue
                value = f"{self.no_category_description if cog['name'] == self.no_category_name else cog['description']}\n"
                for interaction in data:
                    in_blacklist = False
                    if self.blacklist:
                        for black in self.blacklist:
                            if (
                                black in interaction["name"]
                                or black in interaction["cog"]["name"]
                            ):
                                in_blacklist = True
                                break
                    if in_blacklist:
                        continue
                    if interaction["cog"]["name"] == cog["name"]:
                        cog["interactions"].append(interaction)
                        value += f"`{'/' if interaction['type'] in ['slash command', 'subcommand', 'subcommand group',] else '' if 'menu' in interaction['type'] else (self.bot.command_prefix if self.prefix is None else self.prefix)}{interaction['name']}`, "
                value = value[:-2] if value.endswith(", ") else value
                first_page.add_field(name=cog["name"], value=value, inline=False)
            for cog in cogs:
                in_blacklist = False
                if self.blacklist:
                    for black in self.blacklist:
                        if black in cog["name"]:
                            in_blacklist = True
                            break
                if in_blacklist:
                    continue
                for i in range(0, len(cog["interactions"]), self.fields_per_embed):
                    next_page = Embed(
                        title=f"{cog['name']} {i + 1} - {i + self.fields_per_embed}",
                        description=self.no_category_description
                        if cog["name"] == self.no_category_name
                        else cog["description"],
                        colour=self.colour,
                    )
                    for cmd in cog["interactions"][i : (i + self.fields_per_embed)]:
                        cmd_name = cmd["name"]
                        cmd_desc = cmd["description"]
                        cmd_opts = cmd["options"] if "options" in cmd.keys() else []
                        theres_dpy = "\n"
                        if self.dpy_command and cmd_name in duplicates.keys():
                            theres_dpy = (
                                f"\nYou can also use `{(self.bot.command_prefix if self.prefix is None else self.prefix)}{cmd_name}`\n"
                                if not isinstance(cmd_opts, (str, type(None)))
                                else f"\nYou can also use `/{cmd_name}`\n"
                            )
                        desc = (
                            (
                                "No description"
                                if cmd_desc is None or cmd_desc == [] or cmd_desc == ""
                                else cmd_desc
                            )
                            + theres_dpy
                            + "How to use:"
                        )
                        how_to_use = f"\n```\n{'/' if not isinstance(cmd_opts, (str, type(None))) else ('Right click on a ' + cmd['type'].replace(' menu', '')) if 'menu' in cmd['type'] else (self.bot.command_prefix if self.prefix is None else self.prefix)}{'' if 'menu' in cmd['type'] else cmd_name} "
                        if not isinstance(cmd_opts, (str, type(None))):
                            for option in cmd_opts:
                                _type = typer_dict(
                                    option["type"],
                                    option["choices"]
                                    if "choices" in option.keys()
                                    else [],
                                )
                                how_to_use += f"[{option['name']}: {'optional ' if not option['required'] else ''}{_type}], "
                        elif cmd_opts is None:
                            pass
                        else:
                            how_to_use += cmd_opts
                        how_to_use = (
                            how_to_use[:-2] if how_to_use.endswith(", ") else how_to_use
                        )
                        how_to_use += "\n```"
                        next_page.add_field(
                            name=cmd_name, value=desc + how_to_use, inline=False
                        )
                    if self.footer is not None:
                        next_page.set_footer(text=self.footer)
                    embeds.append(next_page)
            await Paginator(
                bot=self.bot,
                ctx=ctx,
                pages=embeds,
                timeout=self.timeout,
                useFirstLast=self.extended_buttons,
                useSelect=self.use_select,
                authorOnly=self.author_only,
            ).run()

    async def async_all_commands(self, guild_id=None):
        result = await get_all_commands(self.bot.user.id, self.token)
        result = [] if result is None else result
        if self.guild_ids or guild_id:
            guild_id = self.guild_ids[0] if guild_id is None else guild_id
            guild_commands = await get_all_commands(
                self.bot.user.id, self.token, guild_id
            )
            result.append(guild_commands) if guild_commands is not None else None
        result = list(filter(lambda x: x is not None, result))
        if not result:
            raise CommandsNotFound
        return result

    async def async_separated(self, guild_id=None):
        all_commands = await self.async_all_commands(guild_id)
        commands, subcommands, menus = [], [], []
        guild_ids_index = None
        for command in all_commands:
            if isinstance(command, list):
                guild_ids_index = all_commands.index(command)
                break
            if command["type"] == 1:
                if "options" in command.keys() and command["options"][0]["type"] in (
                    1,
                    2,
                ):
                    subcommands.append(command)
                else:
                    if "options" not in command.keys():
                        command["options"] = []
                    commands.append(command)
            else:
                menus.append(command)
        if guild_ids_index is not None:
            for command in all_commands[guild_ids_index]:
                if command["type"] == 1:
                    if "options" in command.keys() and command["options"][0][
                        "type"
                    ] in (
                        1,
                        2,
                    ):
                        subcommands.append(command)
                    else:
                        if "options" not in command.keys():
                            command["options"] = []
                        commands.append(command)
                else:
                    menus.append(command)
        master = []
        for command in commands:
            the_cog = getattr(self.slash.commands[command["name"]], "cog", None)
            cog_name = (
                self.no_category_name if the_cog is None else the_cog.qualified_name
            )
            cog_desc = (
                self.no_category_description if the_cog is None else the_cog.description
            )
            master.append(
                {
                    "name": command["name"],
                    "description": command["description"],
                    "options": command["options"],
                    "type": "slash command",
                    "cog": {"name": cog_name, "description": cog_desc},
                }
            )
        for subcommand in subcommands:
            for sub in subcommand["options"]:
                if sub["type"] == 1:
                    try:
                        _ = sub["options"]
                    except KeyError:
                        sub["options"] = []
                    the_cog = getattr(
                        self.slash.subcommands[subcommand["name"]][sub["name"]],
                        "cog",
                        None,
                    )
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    cog_desc = (
                        self.no_category_description
                        if the_cog is None
                        else the_cog.description
                    )
                    master.append(
                        {
                            "name": f'{subcommand["name"]} {sub["name"]}',
                            "description": sub["description"],
                            "options": sub["options"],
                            "type": "subcommand",
                            "cog": {"name": cog_name, "description": cog_desc},
                        }
                    )
                else:
                    try:
                        _ = sub["options"][0]["options"]
                    except KeyError:
                        sub["options"][0]["options"] = []
                    the_cog = getattr(
                        self.slash.subcommands[subcommand["name"]][sub["name"]][
                            sub["options"][0]["name"]
                        ],
                        "cog",
                        None,
                    )
                    cog_name = (
                        self.no_category_name
                        if the_cog is None
                        else the_cog.qualified_name
                    )
                    cog_desc = (
                        self.no_category_description
                        if the_cog is None
                        else the_cog.description
                    )
                    master.append(
                        {
                            "name": f'{subcommand["name"]} {sub["name"]} {sub["options"][0]["name"]}',
                            "description": sub["options"][0]["description"],
                            "options": sub["options"][0]["options"],
                            "type": "subcommand group",
                            "cog": {"name": cog_name, "description": cog_desc},
                        }
                    )

        for menu in menus:
            master.append(
                {
                    "name": menu["name"],
                    "description": menu["description"],
                    "type": ("user menu" if menu["type"] == 2 else "message menu"),
                    "cog": {
                        "name": self.no_category_name,
                        "description": self.no_category_description,
                    },
                }
            )
        for interaction in master:
            if "options" in interaction.keys() and interaction["options"]:
                for option in interaction["options"]:
                    if "required" not in option.keys():
                        option["required"] = False
        return master
