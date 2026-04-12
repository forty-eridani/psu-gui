from src.command.CommandController import CommandDictionary, CommandController 
from src.ErrorMessage import Error
from operator import attrgetter
import threading
import time

class CommandedOutput:
    def __init__(self, seconds: float, command: tuple[str, int, bool], arg: str | None, name: str, is_step: bool, step_to: bool):
        self.seconds = seconds
        self.command = command
        self.arg = arg
        self.name = name
        self.is_step = is_step
        self.step_to = step_to # Whether this command should be interpolated to

    def get_time(self) -> float:
        return self.seconds
    
    def has_arg(self) -> bool:
        return self.arg != None
    
    def __str__(self) -> str:
        return '{' + f"seconds: {self.seconds}, command: {self.command}, arg: {self.arg}, name: {self.name}, is_step: {self.is_step}" + '}'

    def run(self) -> str:
        return CommandController.run_command(self.command, self.arg if self.arg != None else "")

class CommandSchedulerClass:
    def __init__(self, step_rate: float):
        self.commands: list[CommandedOutput] = []
        self.step_rate = step_rate
        self.is_running = False
        self.threads: list[threading.Timer] = []

        self.start_time = -1
        self.pause_time = 0.0
        self.pause_duration = 0.0

    # Step rate in steps per second
    def add_command(self, seconds: float, command: tuple[str, int, bool], arg: str | None, should_step: bool, name: str) -> None:
        if name == "":
            raise Error("Cannot add a command without a name")

        if (arg == "" or arg == None) and command[1] > 0:
            raise Error(f"Cannon create command '{command[0]}' without an argument.")

        if self.is_running:
            raise Error("Cannot add command while script is running.")

        new_command = CommandedOutput(seconds, command, arg, name, False, should_step)

        if self.find_element(name) != -1:
            raise Error(f"Command {name} already exists")
        if (command[1] < 2 and should_step == True):
            raise Error(f"Unable to step '{command}'.")
        elif (command[1] > 0 and arg == None):
            raise Error(f"'{command[0]}' requires an argument.")
        if (len(self.commands) == 0 and should_step == True):
            raise Error(f"Cannot step when there are no other commands")

        self.push_command(new_command)

        
        index = self.find_element(name)

        last_index, next_index = self.get_surrounding_commands(name, False)

        if next_index != -1 and self.commands[next_index].step_to:
            self.interpolate(index, next_index, self.step_rate, f"INTRP_TO_{self.commands[next_index].name}")

        if last_index != -1 and should_step:
            self.interpolate(last_index, index, self.step_rate, f"INTRP_TO_{name}")

        if last_index == -1 and should_step:
            self.commands.pop(index)
            raise Error("Connect step when this is the first command of the type")

    def remove_command(self, name: str) -> None:

        if name == "":
            raise Error("Cannot remove command without a name")

        if self.is_running:
            raise Error("Cannot remove commands while running.")

        index = self.find_element(name)

        if index == -1:
            raise Error(f"Command '{name}' does not exist.")

        last_index, next_index = self.get_surrounding_commands(name, False)

        had_steps = self.commands[index].step_to

        index = self.find_element(name)
        self.commands.pop(index)
        next_index -= 1

        # Means we removed the last coommand of that type
        if last_index >= 0 and next_index < 0 and had_steps:
            print(f'[Info] Removing steps leading up to removed command \'{name}\'.')

            # Opposite of most normal loops: (index1, index2]
            self.remove_steps(last_index, len(self.commands), self.commands[last_index].command)

        # This means there is probably interpolation commands leading to this that have no `anchor`
        if next_index >= 0 and last_index < 0 and self.commands[next_index].step_to:
            print(f"[Info] Removing interpolation commands leading to command '{self.commands[next_index].name}'")

            # Since we are certain that there are no commands leading to this command, we can just start at the first index. Also
            # the `remove_steps()` assumes that each provided index was a manually entered command, we have start at -1 or it won't
            # get rid of the first interpolation command
            self.remove_steps(-1, next_index, self.commands[next_index].command)

        if (next_index >= 0 and self.commands[next_index].step_to and last_index >= 0):
            # You have to re-interpolate if a command was removed
            print(f"[Info] Re-interpolating between commands '{self.commands[last_index].name}' and '{self.commands[next_index].name}'")
            self.interpolate(last_index, next_index, self.step_rate, f"INTRP_TO_{self.commands[next_index].name}")

    def load_file(self, filename: str) -> None:
        self.commands = []
        file_content = ""

        with open(filename, "r") as file:
            file_content = file.read()

        rows = file_content.split("\n")[:-1] # Ignores newline

        attr_names = rows[0].split(",")
        commanded_outputs = rows[1:]

        for commanded_output_str in commanded_outputs:
            # Just placeholder values
            read_command = CommandedOutput(0, ("", 0, False), None, "", False, False)

            for name, attr in zip(attr_names, commanded_output_str.split(",")):
                
                # If statement for all non-str types
                if name == "is_step" or name == "step_to":
                    setattr(read_command, name, True if attr == "True" else False)
                elif name == "command":
                    setattr(read_command, name, CommandDictionary[attr])
                elif name == "seconds":
                    setattr(read_command, name, float(attr))
                else:
                    setattr(read_command, name, attr)

            self.commands.append(read_command)

    def save_file(self, filename: str) -> None:
        # Basically CSV
        if len(self.commands) == 0:
            raise Error("Cannot save file with zero commands")

        file_txt = ""

        # A crude way to do this, but members beginning with `<` when casted to a string are useless to stick into a CSV
        attrs = [attr for attr in dir(self.commands[0]) if not attr.startswith("__") and not str(getattr(self.commands[0], attr)).startswith("<")]

        file_txt += ",".join(attrs) + '\n'

        for command in self.commands:

            # A very cursed example of list comprehension. This simply pushes an attribute if it doesn't start with a '(', and if it does,
            # split it. This is because the command attribute is a tuple, but we only care about the string in that tuple. The splitting magic
            # simply extracts the command name out of the command tuple string literal
            file_txt += ",".join([str(getattr(command, attr)) if not str(getattr(command, attr)).startswith("(") else str(getattr(command, attr))[2:].split(" ")[0] for attr in attrs]) + '\n'

        with open(filename, "w") as file:
            file.write(file_txt)

    def set_step_rate(self, step_rate: float) -> None:
        self.step_rate = step_rate

    def __str__(self):
        return f"{[str(command) for command in self.commands]}"
    
    # Will return empty array if command doesn't have a plot-able arg
    def get_arg_plot(self, command_type: tuple[str, int, bool]) -> tuple[list[float], list[float]]:
        commands = []
        times = []

        for command in self.commands:
            if command.command == command_type and command.command[1] > 0:

                # This is only to make the type hinting shut up
                assert(command.arg != None)

                commands.append(float(command.arg))
                times.append(float(command.seconds))

        return (times, commands)

    def get_command_times(self, command_type: tuple[str, int, bool]) -> list[str]:
        relevant_commands: list[str] = []
        for command in self.commands:
            if command.command == command_type:
                assert(command.arg != None) # Once again to shut up type hints
                relevant_commands.append(f"[{command.name} at {command.seconds}s] " + command.command[0] + (" " + command.arg if command.command[1] > 0 else "")) # types: ignore

        return relevant_commands

    def clear(self):
        self.commands.clear()

    # Will run all the commands at the specified times. Start time references how late
    # in the program you want to be running the specified commands
    def run_commands(self, start_time: float) -> None:
        if self.start_time < 0:
            self.start_time = time.monotonic()
            # print("Setting monotonic clock to", str(self.start_time))

        if self.is_running == False:
            for i in range(len(self.commands) - 1):
                if self.commands[i].seconds >= start_time:
                    thread = threading.Timer(self.commands[i].seconds - start_time, self.commands[i].run)
                    thread.start()

                    self.threads.append(thread)

            # Getting around python not letting me have multiple statements in a lambda :(
            thread = threading.Timer(self.commands[len(self.commands) - 1].seconds - start_time, lambda: (self.commands[len(self.commands) - 1].run(), self.stop_running()))
            thread.start()
            self.threads.append(thread)

        self.is_running = True

    def stop_running(self, on_pause: bool = False) -> None:
        for thread in self.threads:
            thread.cancel()

        self.threads = []

        self.is_running = False

        if not on_pause:
            self.start_time = -1
            self.pause_time = 0.0
            self.pause_duration = 0.0

    def pause(self):
        assert(self.is_running)

        self.stop_running(on_pause=True)
        self.pause_time = time.monotonic()
        # print("Paused at " + str(self.pause_time - self.start_time) + " seconds while start time is " + str(self.start_time))

    def resume(self):
        assert(not self.is_running)
        cur_time = time.monotonic()
        self.pause_duration += cur_time - self.pause_time
        cur_script_time = (cur_time - self.start_time) - self.pause_duration

        # print("Resuming at " + str(cur_script_time) + " seconds.")
        self.run_commands(cur_script_time)

    def push_command(self, command: CommandedOutput) -> None:
        self.commands.append(command)
        self.commands = sorted(self.commands, key=attrgetter('seconds'))

    def get_surrounding_commands(self, name: str, include_steps: bool) -> tuple[int, int]:
        next_index = -1
        last_index = -1

        index = self.find_element(name)
        
        i = index + 1
        while i < len(self.commands) and (self.commands[i].command != self.commands[index].command or (self.commands[i].is_step if not include_steps else True)):
            i += 1
        
        if i < len(self.commands):
            next_index = i

        # Finding the last index of the same command type. `should_step` only indicates that we should interpolate
        # to this command, not from this command to the next. 
        
        i = index - 1
        while i >= 0 and (self.commands[i].command != self.commands[index].command or (self.commands[i].is_step if not include_steps else True)):
            i -= 1

        if i > -1:
            last_index = i

        return (last_index, next_index)

    # The interpolation routine :) Assumes indices refer to same command type
    def interpolate(self, index1: int, index2: int, step_rate: float, name: str) -> None:
        assert(index1 < index2)
        assert(index1 >= 0)
        assert(index2 < len(self.commands))
        assert(self.commands[index1].command == self.commands[index2].command)
        assert(self.commands[index1].arg != None)
        assert(self.commands[index2].arg != None)
        assert(self.commands[index1].command[1] > 1)
        assert(self.commands[index1].seconds != self.commands[index2].seconds)

        # Assuring that we aren't trying to interpolate between points that have intermediaries between 'em
        assert(False not in [command.is_step and command.command == self.commands[index1].command for command in self.commands[index1 + 1:index2]])

        # We want to get rid of any step commands that already existed between the new indices

        index2 -= self.remove_steps(index1, index2, self.commands[index1].command)

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

            new_command = CommandedOutput(new_time, self.commands[index1].command, str(new_arg), name, True, False)
            self.push_command(new_command)

    # Returns the amount of steps removed
    def remove_steps(self, index1: int, index2: int, command_type: tuple[str, int, bool]) -> int:
        assert(index1 < index2)

        pop_count = 0
        for i in range(index2 - 1, index1, -1):
            if self.commands[i].command == command_type:
                self.commands.pop(i)
                pop_count += 1

        return pop_count

    def find_element(self, name: str) -> int:
        for i in range(len(self.commands)):
            if (self.commands[i].name == name):
                return i
            
        return -1

# One step per second is default step rate
CommandScheduler = CommandSchedulerClass(1)
