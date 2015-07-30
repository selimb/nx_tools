# NX Tools

## What is this?

A command-line utility to automate repetitive NX management tasks.

### Commands
* **Updater**: Keep kits and patches up to date.
* **Launcher**: Launch given NX kit with given patch.
* **Identifier**: Identification of current NX process (kit, patch, NX version) via custom hotkey.

### Features
* **Auto-Update**: Ensure you're running the latest and greatest version of NX Tools.
* **Cross-Shell**: Prefer to use Cygwin, GnuNT Bash over Windows CMD? No problem.
* **Support for Windows Task Scheduler**

## Install

Navigate to `T:\selimb\nx_tools` and run `install.bat`. Alternatively, you can run the following from the Windows Run dialog.
```
T:\selimb\nx_tools\install.bat
```
Next, you should configure it for your machine:
```
nx_tools config init
```

## Usage

#### Getting Started
NX Tools is a UNIX-style command line application. Run the following to get a list of the available commands:
```bash
nx_tools --help
```
The `-h` or ``--help`` flag can be appended to any command to read about a specific subcommand.

NX Tools can also be run via `nxt` instead of `nx_tools`.

#### Updater
The updater can be run like this:
```bash
nx_tools update nx11
```
If a new patch and/or build is available, it will be downloaded and extracted. 

#### Launcher
The launcher is run like so:
```bash
nx_tools launch nx11
```
`UGII_TMG_DIR` is not permanently modified.

Should you wish to launch NX with the current `UGII_TMG_DIR` or with NX's internal (vanilla) TMG, you can pass `--vanilla` and `--env-var` options respectively.

*New in 1.1.0*: You can use the `start_in` key in the configuration to set the working directory -- equivalent to "Start in:" in a Windows Shortcut.

*New in 1.1.4*: Launch NX with a `--name` to tag the process. This shows up in the [Identifier](#identifier) as the window title.

#### Identifier
The Identifier allows you to query the Build and Patch for active NX processes with the use of a user-defined hotkey -- *F9* by default -- provided NX was launched with the *NX Tools* Launcher. The hotkey can be defined in the configuration file. 

If NX is the active window when the hotkey is pressed, build/patch data is only given for said active window. Otherwise, the Identifier will cycle through the build/patch data for all active NX processes. You can use <Tab> or the user-defined shortcut to keep cycling through, or <Escape> to stop. 

The identification feature is accessed through an [AutoHotkey](http://www.autohotkey.com/) executable (no installation required). The Identifier can be launched with:
```
nx_tools identifier
```
It will stay active in the tray (notification area) and enable the hotkey as long as it is active, i.e. you do not need to run it everytime you want to use the hotkey. 

#### Task Scheduler

You can import the task into Windows' Task Scheduler by invoking:
```
nx_tools add_task
```
You will be prompted for your User Account password. 

The task is scheduled to check for NX11 updates every hour. If an update for the patch or build is found, you are prompted whether to fetch it -- the prompt times out after 10 seconds, in which case it acts as **Yes**.

Should you wish to modify it you can edit the *Update NX11* task in the **Task Scheduler**, which you can open by running
```cmd
%SYSTEMROOT%\System32\taskschd.msc
```

## I don't like having to run commands through the command-line

Simple batch files are provided in `T:\selimb\nx_tools\sample_batch` so that you don't have to manually enter the command-line. You may copy those anywhere you want on your machine. If you create shortcuts, you can even pin those to taskbar or start menu!

## Configuration

*NX Tools* can be edited manually by calling:
```
nx_tools config edit
```

#### Hotkeys
AutoHotkey defines the hotkey symbols as such:

| Symbol   | Description            |
|----------|------------------------|
| #        | Win (Windows logo key) |
| !        | Alt                    |
| ^        | Control                |
| +        | Shift                  |
| [a-zA-Z] | Any letter             |
| F[1-12]  | Function key           |

For instance, **!^s** will set the hotkey to **Control + Alt + S**. 

#### Revert to defaults
In the case where you screw up your configuration and want to revert to the defaults:
* `nx_tools config update`: Update **empty** items with defaults.
* `nx_tools config reset`: Reset all items to defaults. 

## Bugs / Feature Requests

You can submit bugs and feature requests on this [project's Issues](https://github.com/beselim/nx_tools/issues) if you already have a GitHub account! Alternatively, you can send me an [e-mail](mailto:selim.belhaouane@gmail.com).

If you submit a bug, I would appreciate if you could attach your config file along with a snapshot of the command prompt.

If you found any part of the README confusing, improvements to the documentation are very much welcome and appreciated. 
