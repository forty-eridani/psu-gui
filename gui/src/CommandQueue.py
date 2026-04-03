import serial
from enum import Enum
import threading

# Stores tuples where first is the string and second is whether it takes an arg
# The "_REQ" indicates that the command ends with a question mark
class Command(Enum):
    # Initialization Control Commands
    ADR = ("ADR ", True)
    CLS = ("CLS", False)
    RST = ("RST", False)
    RMT = ("RMT?", False)
    MDAV_REQ = ("MDAV?", False)
    SLASH = ("\\", False)

    # ID control commands
    IDN_REQ = ("IDN?", False)
    REV_REQ = ("REV?", False)
    SN_REQ = ("SN?", False)
    DATE_REQ = ("DATE?", False)

    # Output control commands
    PV = ("PV ", True)
    PV_REQ = ("PV?", False)
    MV_REQ = ("MV?", False)
    PC = ("PC ", True)
    PC_REQ = ("PC?", False)
    MC_REQ = ("MC?", False)
    DVC_REQ = ("DVC?", False)
    OUT = ("OUT ", True)
    OUT_REQ = ("OUT?", False)
    FLD = ("FLD ", True)
    FLD_REQ = ("FLD?", False)
    FBD = ("FBD ", True)
    FBD_REQ = ("FBD?", False)
    FBDRST = ("FBDRST", False)
    OVP = ("OVP ", True)
    OVP_REQ = ("OVP?", False)
    OVM = ("OVM?", False)
    UVL = ("UVL ", True)
    UVL_REQ = ("UVL?", False)
    AST = ("AST ", True)
    AST_REQ = ("AST?", False)
    SAV = ("SAV", False)
    RCL = ("RCL", False)
    MODE_REQ = ("MODE?", False)
    MS = ("MS?", False)

    # Global Output Commands
    GPRST = ("GRST", False)
    GPV = ("GPV ", True)
    GPC = ("GPC ", True)
    GOUT = ("GOUT", False)
    GSAV = ("GSAV", False)
    GRCL = ("GRCL", False)

    # Status Control Commands
    STT_REQ = ("STT?", False)
    FLT_REQ = ("FLT?", False)
    FENA = ("FENA", False)
    FENA_REQ = ("FENA?", False)
    FEVE_REQ = ("FEVE?", False)
    STAT_REQ = ("STAT?", False)
    SENA = ("SENA", False)
    SENA_REQ = ("SENA?", False)
    SEVE_REQ = ("SEVE", False)

class CommandQueueClass:
    def __init__(self, address, port):
        self.ser = serial.serial_for_url(f"{address}:{port}")
        self.command_queue = []
        self.mutex = threading.Lock()

    def run_command(self, command: tuple[str, bool], arg: str) -> str:
        real_command = command[0]
        result = ""

        if (command[1] == True):
            real_command += arg

        # Just in case requests come from multiple threads
        with self.mutex:
            print(f"Sending '{real_command}\r'...")
            self.ser.write(f"{real_command}\r".encode())
            result = self.ser.readline().decode()

        return result 

    # Runs the raw text param as a command. Must be terminated with carriage return
    def run_raw_command(self, command: str) -> str:
        result = None

        with self.mutex:
            self.ser.write(command.encode())
            result = self.ser.readline().decode()

        return result

    def __del__(self):
        self.ser.close()

# Singleton Pattern 
CommandQueue = CommandQueueClass("127.0.0.1", "4000")
