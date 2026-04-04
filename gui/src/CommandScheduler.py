from CommandController import Command
from operator import attrgetter

class CommandedOutput:
    def __init__(self, seconds: float, command: tuple[str, int], arg: str | None, name: str, is_step: bool):
        self.seconds = seconds
        self.command = command
        self.arg = arg
        self.name = name
        self.is_step = is_step

    def get_time(self) -> float:
        return self.seconds
    
    def has_arg(self) -> bool:
        return self.arg == None
    
    def __str__(self) -> str:
        return '{' + f"seconds: {self.seconds}, command: {self.command}, arg: {self.arg}, name: {self.name}, is_step: {self.is_step}" + '}'
    
class CommandSchedulerClass:
    def __init__(self, step_rate: float):
        self.commands: list[CommandedOutput] = []
        self.step_rate = step_rate

    # Step rate in steps per second
    def add_command(self, seconds: float, command: tuple[str, int], arg: str | None, should_step: bool, name: str) -> None:
        new_command = CommandedOutput(seconds, command, arg, name, False)

        if self.find_element(name) != -1:
            print(f"[Error] Command {name} already exists")
            return
        
        self.push_command(new_command)

        if (command[1] < 2 and should_step == True):
            print(f"[Error] Unable to step '{command}'.")
            return
        elif (command[1] > 0 and arg == None):
            print(f"[Error] '{command[0]}' requires an argument.")
            return
        elif (len(self.commands) == 1 and should_step == True):
            print(f"[Warning] Cannot step when there is only one element in the commands")
            return

        if (should_step):
            index = self.find_element(name)

            # Finding next index of the same command type
            next_index = None
            last_index = None
            
            i = index + 1
            while i < len(self.commands) and self.commands[i].command != self.commands[index].command:
                i += 1
            
            if i < len(self.commands):
                next_index = i

            # Finding the last index of the same command type
            i = index - 1
            while i >= 0 and self.commands[i].command != self.commands[index].command:
                i -= 1

            if i > -1:
                last_index = i

            if next_index != None:
                self.interpolate(index, next_index, self.step_rate, f"INTRP_{name}")

            if last_index != None:
                self.interpolate(last_index, index, self.step_rate, f"INTRP_{name}")

            if last_index == None and next_index == None:
                print("[Warning] Cannot step when there is only one command of the type")

    def remove_command(self, name: str) -> None:
        pass

    def load_file(self, filename: str) -> None:
        pass

    def save_file(self, filename: str) -> None:

        # Basically CSV
        pass

    def set_step_rate(self, step_rate: float) -> None:
        self.step_rate = step_rate

    def __str__(self):
        return f"[ {[str(command) for command in self.commands]} ]"

    def push_command(self, command: CommandedOutput) -> None:
        self.commands.append(command)
        self.commands = sorted(self.commands, key=attrgetter('seconds'))

    # The interpolation routine :) Assumes indices refer to same command type
    def interpolate(self, index1: int, index2: int, step_rate: float, name: str) -> None:
        assert(index1 < index2)
        assert(index1 >= 0)
        assert(index2 < len(self.commands))
        assert(self.commands[index1].command == self.commands[index2].command)
        assert(self.commands[index1].arg != None)
        assert(self.commands[index2].arg != None)
        assert(self.commands[index1].command[1] > 1)

        step_count: int = int((self.commands[index2].seconds - self.commands[index1].seconds) * step_rate)
        step_interval: float = (self.commands[index2].seconds - self.commands[index1].seconds) / step_count

        initial_seconds = self.commands[index1].seconds

        arg1 = float(self.commands[index1].arg) # type: ignore Let's just say we ALREADY ASSERTED THAT ARG CANNOT BE NONE
        arg2 = float(self.commands[index2].arg) # type: ignore

        delta_arg = arg2 - arg1
        arg_step = delta_arg / step_count

        # Excluding the nodes that already exist
        for i in range(1, step_count):
            new_time = initial_seconds + i * step_interval
            new_arg = arg1 + i * arg_step

            # Means arg must be an integer
            if self.commands[index1].command[1] == 2:
                new_arg = int(new_arg)

            new_command = CommandedOutput(new_time, self.commands[index1].command, str(new_arg), name, True)
            self.push_command(new_command)


    def find_element(self, name: str) -> int:
        for i in range(len(self.commands)):
            if (self.commands[i].name == name):
                return i
            
        return -1

# One is default step rate
CommandScheduler = CommandSchedulerClass(1)