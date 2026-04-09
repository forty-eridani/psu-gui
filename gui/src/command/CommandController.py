import serial
from enum import Enum
import threading

# Stores tuples where first is the string and second arg tells arg behavior:
# 0: No argument
# 1: Argument that cannot be interpolated
# 2: Integer argument that can be interpolated
# 3: Decimal argument that can be interpolated
# The next boolean indicates whether the command returns something other than OK
# The "_REQ" indicates that the command ends with a question mark
class Command:
    # Initialization Control Commands
    ADR = ("ADR ", 1, False)
    CLS = ("CLS", 0, False)
    RST = ("RST", 0, False)
    RMT = ("RMT", 1, False)
    RMT_REQ = ("RMT?", 0, True)
    MDAV_REQ = ("MDAV?", 0, True)

    # ID control commands
    IDN_REQ = ("IDN?", 0, True)
    REV_REQ = ("REV?", 0, True)
    SN_REQ = ("SN?", 0, True)
    DATE_REQ = ("DATE?", 0, True)

    # Output control commands
    PV = ("PV ", 3, False)
    PV_REQ = ("PV?", 0, True)
    MV_REQ = ("MV?", 0, True)
    PC = ("PC ", 3, False)
    PC_REQ = ("PC?", 0, True)
    MC_REQ = ("MC?", 0, True)
    DVC_REQ = ("DVC?", 0, True)
    OUT = ("OUT ", 1, False)
    OUT_REQ = ("OUT?", 0, True)
    FLD = ("FLD ", 1, False)
    FLD_REQ = ("FLD?", 0, True)
    FBD = ("FBD ", 2, False)
    FBD_REQ = ("FBD?", 0, True)
    FBDRST = ("FBDRST", 0, False)
    OVP = ("OVP ", 3, False)
    OVP_REQ = ("OVP?", 0, True)
    OVM = ("OVM", 0, False)
    OVM = ("OVM?", 0, True)
    UVL = ("UVL ", 3, False)
    UVL_REQ = ("UVL?", 0, True)
    AST = ("AST ", 1, False)
    AST_REQ = ("AST?", 0, True)
    SAV = ("SAV", 0, False)
    RCL = ("RCL", 0, False)
    MODE_REQ = ("MODE?", 0, True)
    MS = ("MS?", 0, True)

    # Global Output Commands
    GPRST = ("GRST", 0, False)
    GPV = ("GPV ", 3, False)
    GPC = ("GPC ", 3, False)
    GOUT = ("GOUT", 0, False)
    GSAV = ("GSAV", 0, False)
    GRCL = ("GRCL", 0, False)

    # Status Control Commands
    STT_REQ = ("STT?", 0, True)
    FLT_REQ = ("FLT?", 0, True)
    FENA = ("FENA", 0, False)
    FENA_REQ = ("FENA?", 0, True)
    FEVE_REQ = ("FEVE?", 0, True)
    STAT_REQ = ("STAT?", 0, True)
    SENA = ("SENA", 0, False)
    SENA_REQ = ("SENA?", 0, True)
    SEVE_REQ = ("SEVE", 0, False)

# This array was made with some creative uses of ctrl-f, so this should probably be tested
CommandDictionary = {
    "ADR": ("ADR ", 1, False),
    "CLS": ("CLS", 0, False),
    "RST": ("RST", 0, False),
    "RMT": ("RMT?", 0, True),
    "MDAV?": ("MDAV?", 0, True),

    # ID control commands
    "IDN?": ("IDN?", 0, True),
    "REV?": ("REV?", 0, True),
    "SN?": ("SN?", 0, True),
    "DATE?": ("DATE?", 0, True),

    # Output control commands
    "PV": ("PV ", 3, False),
    "PV?": ("PV?", 0, True),
    "MV?": ("MV?", 0, True),
    "PC": ("PC ", 3, False),
    "PC?": ("PC?", 0, True),
    "MC?": ("MC?", 0, True),
    "DVC?": ("DVC?", 0, True),
    "OUT": ("OUT ", 1, False),
    "OUT?": ("OUT?", 0, True),
    "FLD": ("FLD ", 1, False),
    "FLD?": ("FLD?", 0, True),
    "FBD": ("FBD ", 2, False),
    "FBD?": ("FBD?", 0, True),
    "FBDRST": ("FBDRST", 0, False),
    "OVP": ("OVP ", 3, False),
    "OVP?": ("OVP?", 0, True),
    "OVM": ("OVM", 0, False),
    "UVL": ("UVL ", 3, False),
    "UVL?": ("UVL?", 0, True),
    "AST": ("AST ", 1, False),
    "AST?": ("AST?", 0, True),
    "SAV": ("SAV", 0, False),
    "RCL": ("RCL", 0, True),
    "MODE?": ("MODE?", 0, True),
    "MS?": ("MS?", 0, True),

    # Global Output Commands
    "GPRST": ("GRST", 0, False),
    "GPV": ("GPV ", 3, False),
    "GPC": ("GPC ", 3, False),
    "GOUT": ("GOUT", 1, False),
    "GSAV": ("GSAV", 0, False),
    "GRCL": ("GRCL", 0, True),

    # Status Control Commands
    "STT?": ("STT?", 0, True),
    "FLT?": ("FLT?", 0, True),
    "FENA": ("FENA", 0, False),
    "FENA?": ("FENA?", 0, True),
    "FEVE?": ("FEVE?", 0, True),
    "STAT?": ("STAT?", 0, True),
    "SENA": ("SENA", 0, False),
    "SENA?": ("SENA?", 0, True),
    "SEVE?": ("SEVE", 0, True),
} 

class CommandControllerClass:
    def __init__(self, address, port):
        self.ser = serial.serial_for_url(f"{address}:{port}")
        self.command_queue = []
        self.mutex = threading.Lock()

        # Can be set as a callback whenever a command is run. Must take two 
        # strings as arguments: one for the command and one for the response
        self.on_command = None
        print(f"Opened socket at {address}:{port}")

    def run_command(self, command: tuple[str, int, bool], arg: str) -> str:
        real_command = command[0]
        result = ""

        if (command[1] == True):
            real_command += arg

        print(f"Sending '{real_command}'src..")
        result = self.run_raw_command(real_command + arg + "\r")

        if self.on_command != None:
            self.on_command(real_command, result)

        return result 
    
    # Sets the function called when commands are run. Function must take 
    # two strings as arguments: one for the command and one for the response
    def set_on_command(self, on_command) -> None:
        self.on_command = on_command

    # Runs the raw text param as a command. Must be terminated with carriage return
    def run_raw_command(self, command: str) -> str:
        result = None

        # Just in case requests come from multiple threads
        with self.mutex:
            self.ser.write(command.encode())
            result = self.ser.readline().decode()

        return result

    def get_status(self):
        pass

    def __del__(self):

        if (hasattr(self, "ser")):
            print("Closing socket") 
            self.ser.close()

# Singleton Pattern 

try:
    CommandController = CommandControllerClass("socket://127.0.0.1", "4000")
except:
    print("[Error] Could not create command controller singleton")
    CommandController = None
