# Ch-ch-ch-ch-changes

## 1.1.0

Add `start_in` key in config (`null` by default). This sets the working directory whenever you launch NX. 

## 1.0.0

Completely revamped the CLI, configuration management, deployment. Users no longer run a batch file in their PATH, since that wouldn't work for BASH users. 

Many options added. Run `nx_tools --help` for a list of them. 

## 0.3.0

Complete refactor of Updaters. Task Scheduler now checks if anything new is available before prompting. 

## 0.2.0

New Feature: Task Scheduler integration with Updater.


## 0.1.4

Default configuration now shows examples of Frozen NX Versions.

## 0.1.3

The goal of this release was to improve TMG patch selection. Users now have to the choice to either: not touch `UGII_TMG_DIR` at all or set it to blank. 

Not setting `UGII_TMG_DIR` means that the current value of the variable will be used. This can be done by passing **user** to the Launcher when prompted for a patch. 

On the other hand, setting the variable to blank will tell NX to use its internal *cae_extras*. This can be done by:
* Passing an empty field to the Launcher when prompted for a patch. 
* Not setting a **patch** directory specified for a given NX version in the configuration file. 

## 0.1.2

Allow "11" to be passed to launcher as an alternative to "nx11".

## 0.1.1

Fix bug where the Updater crashes when more than one TMG windows patch is found on the FTP server. 

The user will now be prompted to select which one he wants if more than one new patch is found.
 
## 0.1.0

The goal of this release was to allow the user to:

* Use frozen NX builds from the Y:\ drive. If the full path of the 
`ugraf` executable is given, the build cannot be updated but will
be launched automatically when calling that particular version. 
* Not have to specify a TMG patch -- leave blank input. Consequently, 
UGII_TMG_DIR will not be set for the process. This may be useful for running 
frozen builds with the native patch.

Other fixes:
* Luc sometimes has more than one kit in his *T* drive. When this happens, the
tool either fetches the kit that is not already owned or asks for input, depending
on the number of not-owned kits. 

## 0.0.0

Initial Release