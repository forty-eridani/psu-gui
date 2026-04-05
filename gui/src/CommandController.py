import serial
from enum import Enum
import threading

# Stores tuples where first is the string and second arg tells arg behavior:
# 0: No argument
# 1: Argument that cannot be interpolated
# 2: Integer argument that can be interpolated
# 3: Decimal argument that can be interpolated
# The "_REQ" indicates that the command ends with a question mark
class Command:
    # Initialization Control Commands
    ADR = ("ADR ", 1)
    CLS = ("CLS", 0)
    RST = ("RST", 0)
    RMT = ("RMT?", 0)
    MDAV_REQ = ("MDAV?", 0)
    SLASH = ("\\", 0)

    # ID control commands
    IDN_REQ = ("IDN?", 0)
    REV_REQ = ("REV?", 0)
    SN_REQ = ("SN?", 0)
    DATE_REQ = ("DATE?", 0)

    # Output control commands
    PV = ("PV ", 3)
    PV_REQ = ("PV?", 0)
    MV_REQ = ("MV?", 0)
    PC = ("PC ", 3)
    PC_REQ = ("PC?", 0)
    MC_REQ = ("MC?", 0)
    DVC_REQ = ("DVC?", 0)
    OUT = ("OUT ", 1)
    OUT_REQ = ("OUT?", 0)
    FLD = ("FLD ", 1)
    FLD_REQ = ("FLD?", 0)
    FBD = ("FBD ", 2)
    FBD_REQ = ("FBD?", 0)
    FBDRST = ("FBDRST", 0)
    OVP = ("OVP ", 3)
    OVP_REQ = ("OVP?", 0)
    OVM = ("OVM?", 0)
    UVL = ("UVL ", 3)
    UVL_REQ = ("UVL?", 0)
    AST = ("AST ", 1)
    AST_REQ = ("AST?", 0)
    SAV = ("SAV", 0)
    RCL = ("RCL", 0)
    MODE_REQ = ("MODE?", 0)
    MS = ("MS?", 0)

    # Global Output Commands
    GPRST = ("GRST", 0)
    GPV = ("GPV ", 3)
    GPC = ("GPC ", 3)
    GOUT = ("GOUT", 0)
    GSAV = ("GSAV", 0)
    GRCL = ("GRCL", 0)

    # Status Control Commands
    STT_REQ = ("STT?", 0)
    FLT_REQ = ("FLT?", 0)
    FENA = ("FENA", 0)
    FENA_REQ = ("FENA?", 0)
    FEVE_REQ = ("FEVE?", 0)
    STAT_REQ = ("STAT?", 0)
    SENA = ("SENA", 0)
    SENA_REQ = ("SENA?", 0)
    SEVE_REQ = ("SEVE", 0)

# This array was made with some creative uses of ctrl-f, so this should probably be tested
CommandDictionary = {
    "ADR": ("ADR ", 1),
    "CLS": ("CLS", 0),
    "RST": ("RST", 0),
    "RMT": ("RMT?", 0),
    "MDAV?": ("MDAV?", 0),
    "\\": ("\\", 0),

    # ID control commands
    "IDN?": ("IDN?", 0),
    "REV?": ("REV?", 0),
    "SN?": ("SN?", 0),
    "DATE?": ("DATE?", 0),

    # Output control commands
    "PV": ("PV ", 3),
    "PV?": ("PV?", 0),
    "MV?": ("MV?", 0),
    "PC": ("PC ", 3),
    "PC?": ("PC?", 0),
    "MC?": ("MC?", 0),
    "DVC?": ("DVC?", 0),
    "OUT": ("OUT ", 1),
    "OUT?": ("OUT?", 0),
    "FLD": ("FLD ", 1),
    "FLD?": ("FLD?", 0),
    "FBD": ("FBD ", 2),
    "FBD?": ("FBD?", 0),
    "FBDRST": ("FBDRST", 0),
    "OVP": ("OVP ", 3),
    "OVP?": ("OVP?", 0),
    "OVM": ("OVM?", 0),
    "UVL": ("UVL ", 3),
    "UVL?": ("UVL?", 0),
    "AST": ("AST ", 1),
    "AST?": ("AST?", 0),
    "SAV": ("SAV", 0),
    "RCL": ("RCL", 0),
    "MODE?": ("MODE?", 0),
    "MS": ("MS?", 0),

    # Global Output Commands
    "GPRST": ("GRST", 0),
    "GPV": ("GPV ", 3),
    "GPC": ("GPC ", 3),
    "GOUT": ("GOUT", 0),
    "GSAV": ("GSAV", 0),
    "GRCL": ("GRCL", 0),

    # Status Control Commands
    "STT?": ("STT?", 0),
    "FLT?": ("FLT?", 0),
    "FENA": ("FENA", 0),
    "FENA?": ("FENA?", 0),
    "FEVE?": ("FEVE?", 0),
    "STAT?": ("STAT?", 0),
    "SENA": ("SENA", 0),
    "SENA?": ("SENA?", 0),
    "SEVE?": ("SEVE", 0),
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

    def run_command(self, command: tuple[str, bool], arg: str) -> str:
        real_command = command[0]
        result = ""

        if (command[1] == True):
            real_command += arg

        print(f"Sending '{real_command}'...")
        result = self.run_raw_command(real_command + "\r")

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
