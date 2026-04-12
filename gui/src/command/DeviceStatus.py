from src.command.CommandController import CommandController 
import time

class StatusFrame:
    def __init__(self, command_types: list[tuple[str, int, bool]]):
        self.status = {
            cmd: str(CommandController.run_command(cmd, "")) for cmd in command_types
        }