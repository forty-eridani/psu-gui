from src.command.CommandController import CommandController, CommandDictionary

class DeviceStatusClass:
    def __init__(self):
        self.command_reqs = [cmd[0] for cmd in CommandDictionary.values() if cmd[2] == True]
        self.status = []

    def udpate(self) -> None:
        result = {}

        for name in self.command_reqs:
            res = CommandController.run_command(name, "")

            result[name] = res

        self.status.append(result)

    def get_recent_status(self, elements: int):
        return self.status[-elements:]

    def clear(self):
        self.status.clear()

DeviceStatus = DeviceStatusClass()
