class SlashHelpError(Exception):
    """Base SlashHelp error"""


class NoSlashVar(SlashHelpError):
    def __init__(self):
        super().__init__(
            "No slash variable detected! Please create a slash variable:\n`slash = SlashCommand(bot, sync_commands=True)`"
        )
