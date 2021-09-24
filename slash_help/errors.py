class SlashHelpError(Exception):
    """Base SlashHelp error"""


class CommandsNotFound(SlashHelpError):
    def __init__(self):
        super().__init__(
            "No commands detected! If you are only using guild commands, try specifying the guild id!"
        )
