# psu-gui

## Table of Contents
- [psu-gui](#psu-gui)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Commands](#commands)
    - [Adding Commands](#adding-commands)
    - [Interpolation](#interpolation)
    - [Removing Commands](#removing-commands)
    - [Viewing Numerical Targets](#viewing-numerical-targets)
    - [Viewing the Command Schedule](#viewing-the-command-schedule)
  - [Connecting to a Device](#connecting-to-a-device)
  - [Scripts](#scripts)
    - [Saving and Loading Scripts](#saving-and-loading-scripts)
    - [Running Scripts](#running-scripts)
    - [Script Format](#script-format)
  - [Real Time Viewing](#real-time-viewing)
    - [Viewing Real Time Data](#viewing-real-time-data)
    - [Setting Real Time Parameters](#setting-real-time-parameters)
  - [Consoles](#consoles)
    - [The Manual Console](#the-manual-console)
    - [The Output Console](#the-output-console)
  - [Running the Program](#running-the-program)
    - [The GUI](#the-gui)
    - [The Simulated Backend](#the-simulated-backend)
- [Making Contributions](#making-contributions)

## Introduction

This program is a GUI wrapper around the serial interface for the GEN600-2.6 Programmable Power Supply. This program contains functions for manipulating all parameters of the power supply. You can find the full spec for the serial interface on the [power supply's manual](https://product.tdk.com/system/files/dam/doc/product/power/switching-power/prg-power/instruction_manual/gen1u-750-1500w_user_manual.pdf).

## Commands

### Adding Commands

In order to control the power supply over time, you can use scheduled commands. Every command can be scheduled (even commands that simply return info). To create your own command, locate the `Edit` menu option, and select `Add Command`. You will be greeted with a prompt containing several fields:

- `Command Name`: The name that will be given to the command  
- A dropdown box containing every command  
- `Argument for Command`: This may be grayed out depending on what was selected in the dropdown menu. Some commands don't take arguments while some do. If you chose a command that takes an argument and don't provide one, you will be greeted with an error
- `Time (s)` The time in seconds after starting the script that the command will run in seconds
- `Step`: A checkbox that may not appear if the command doesn't take arguments or doesn't take arguments that can be interpolated. Something like `ADDR` has no reason to be interpolated, so the option isn't provided.
- `Step rate in steps per second`: If you chose for the argument to be interpolated, this field sets the step rate leading to that command. Say you set the voltage to `0v` at 0 seconds and `5v` at 10 seconds and set the step rate to 1 step per second. This means that the program will generate 8 intermediate steps between those commands 

### Interpolation

As mentioned above, commands are able to be interpolated between. Their behavior however is important to note. If you add a command set to be stepped to, several steps will be generated between the last command and the command you have created. This means a command's step state has no bearing on what will happen *after* the command runs.

Another important aspect of this behavior is adding and removing commands. If a command is added in between commands that have been interpolated between, the program will re-generate the interpolation as if the commands had been made chronologically.

### Removing Commands

Commands can also be removed by name. In that same `Edit` menu, there is a `Remove Command` option. Here, you can remove commands by the name you gave them in the `Add Command` prompt. Removing commands will also remove any interpolation to that command that previously existed and re-interpolate to the next command if the next command had the `Step` option enabled.

### Viewing Numerical Targets

To view commands that can be graphed, you can view them on the program's main graph. To change what command target you would like to view, select the `Script Setpoints` submenu under the `View` Menu, and choose which targets you would like to view. If a script is run, you can also view the device's measured values against the script targets. This will appear as a red line that is updated according to the real time update parameters.

### Viewing the Command Schedule

To view scheduled commands that are not graphable, you can use the command schedule. In the `View` menu, select `Script Command Schedule`. In the prompt, you can select the schedule of every single command, including the ones that are graphed. The text will contain the name of the command, the time at which the command will run, and any arguments that the command has.

## Connecting to a Device

In order to connect to a device, select the `File` menu and select the `Connect` option. This will prompt you to give the address and port of the device as this only works for serial *over* a TCP connection. You can also disconnect from the device by selecting `Disconnect` from the `File` menu. You will also note a `Connected •` or `Disconnected •` symbol on the top left to indicate whether a device is actually connected.

## Scripts

### Saving and Loading Scripts

By creating and scheduling commands, you have already essentially written a script. If you would like to save your script, select the `File` menu and `Save Script As`. Similarily, if you would like to load a script, simply go to the `File` menu and select `Load Script`.

### Running Scripts

To run a script, you must be connected to a device or else the `Run` option in the top right will be grayed out. Once you are connected and have a script to run, you can select run and the script will begin running. You can pause the script by selecting `Pause` in the top right. If the script is paused, hitting `Run` will resume where the script left off. If `Stop` is selected, the script will be stopped and hitting `Run` again will restart the script's execution.

### Script Format

The scripts are essentially CSV files. The top row contains the column information indicating the attribute of the command, and the rest of the rows contain the commands. These files are not checked or verified in any way, so ensure that you are only loading files that have been generated by the program.

## Real Time Viewing

### Viewing Real Time Data

To view real time data on the main graph, simply select a parameter from the `Real Time Device Telemetry` submenu in `View`. If there is no connected device, nothing will happen, but if connected, all of the real time graphs will display the real time device information.  

### Setting Real Time Parameters

In order to set Real Time parameters for the Real Time graphs, select the `Real Time Graph Settings` option from the `View` menu. Here, you can adjust the poll rate (the rate at which device information is retrieved), and the Lookback time, which is the window of time that can be viewed at once inside of the real time graphs.

## Consoles

### The Manual Console

If you would like to interact with the device as you would over a normal serial connection, you can use the manual console on the main window. All commands are available to use even during script execution, so be careful in its use. The console is necessary to view the state of the device with anything that cannot be graphed.

### The Output Console

If you want to see all traffic between your computer and the device, you can use the output console found in the `Output Console` item in the `View` menu. This output console will include the traffic from any running scripts as well as manual input from the manual console.

## Running the Program

### The GUI

Because this project is still not quite finished, a release has not been made. In order to run the project, clone the repository and create a virtual python environment in the `gui/` directory using `python -m venv .` and activating it using `source bin/activate` on linux or `Scripts/activate` on windows. Here, you will need to install the packages `PySide6` and `pyqtgraph`. Once these are all installed, you must run the program as a package. To do this, simply enter `python -m src.main` and the program should come alive!

### The Simulated Backend

To test this program, I made a simulated backend in C that uses a berkley socket to connect over TCP to the GUI. The simulated backend isn't completely perfect; for example, you don't have to address the PSU to do anything, nor is there support for checksums to verify commands, however it's good enough to test the functionality of the GUI. To enable the backend, enter the `psu-backend/` directory and make a `build/` directory. Next, run the `make` command to build the executable, and the executable is named `out` in the `build/` directory. Now you can connect to the backend by the address `socket://127.0.0.1` (your PC's local address) and port `4000`.

It is worth noting that not much real "simulation" goes on in this program. It simply keeps track of program state (like if `PV` was run, it will set a voltage state that can be retrieved with `PV?` or `MV?`) and ensures that input is within limits defined in the manual.

# Making Contributions

Feel free to open issues or PRs as you see fit! This is not a complete program and still has quite a ways until being very useful. The program is fairly modular, so changes in script format or real time data formats or logging can be made fairly easily.
