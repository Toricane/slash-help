class SlashHelpError(Exception):
    """Base SlashHelp error"""


class CommandsNotFound(SlashHelpError):
    def __init__(self):
        super().__init__(
            "No commands detected! If you are only using guild commands, try specifying the guild id!"
        )


class NameNeeded(SlashHelpError):
    def __init__(self):
        super().__init__("No bot_name detected! Required if use_subcommand is True!")


class IncorrectName(SlashHelpError):
    def __init__(self):
        super().__init__(
            "Incorrect string passed into bot_name! \nMust match regex ^[\\w-]{1,32}$\nOnly a-z, 0-9, - and _"
        )
