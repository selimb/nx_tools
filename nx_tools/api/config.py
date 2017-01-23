"""
Functions for configuring paths and executable.
Contains defaults.
"""
from __future__ import print_function

import click
import json
import logging
import shutil
import subprocess

from .._click import NamedGroupNoArgs
from ..constants import DEFAULT_CONFIG_PATH, USER_CONFIG_PATH, NPP
from ..exceptions import UserConfigNotFound
from .. import utils

BACKUP_EXT = '.bak'


@click.command('config', cls=NamedGroupNoArgs,
               short_help='Configuration manipulation.')
def cli():
    pass


@cli.command('update',
             short_help="Fill empty user configuration values with defaults.")
def update():
    defaults = utils.read_default_config()
    try:
        user = utils.read_user_config()
    except UserConfigNotFound:
        user = {}
    utils.recursive_dict_update(defaults, user)
    utils.write_json(defaults, USER_CONFIG_PATH)
    print("User configuration updated.")


@cli.command('reset',
             short_help="Completely reset user configuration to defaults.")
def reset():
    shutil.copyfile(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)
    print("Default configuration written to %s" % USER_CONFIG_PATH)


@cli.command('init',
             short_help="Interactively initialize user configuration.")
def init():
    from .. import readline
    import glob
    def pause():
        click.prompt('Press [Enter] to proceed', default='',
                     show_default=False)
    def prompt(text, build_or_patch):
        return click.prompt(
                text.upper(), value_proc=utils.ensure_dir_exists,
                default=config['local'][build_or_patch][text.lower()]
                )
    def complete(text, state):
        return (glob.glob(text+'*')+[None])[state]
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    config = utils.read_config()
    user = config.copy()
    del user['remote']
    del user['7z_exe']
    header = "NX Tools"
    print('')
    print(header)
    print('=' * len(header))
    print("Pressing enter accepts defaults.")
    print("It's ok to input a non-existing directory --"
          " they will be created for you.")
    print("Auto-completion for paths is enabled -- use backslashes.")
    pause()

    print('')
    print("Let's setup your local NX build locations.")
    print("The directory you input should/will contain various NX builds"
          ", which themselves contain a 'kits' folder.")
    print('')
    k = 'build'
    for version in ('nx11', 'nx1003'):
        ans = prompt(version, k)
        user['local'][k][version] = ans
    print("It is not necessary to configure frozen builds"
          " such as NX1001!")
    print("The Launcher detects frozen builds"
          " when the location is an executable.")

    pause()

    print('')
    print("Let's setup your TMG patches locations.")
    print("The directory you input should contain various patches"
          ", which themselves contain a 'tmg' folder.")
    k = 'patch'
    for version in ('nx11', 'nx10', 'nx9'):
        ans = prompt(version, k)
        user['local'][k][version] = ans

    print('')

    print("Finally, let's configure the Identifier.")
    k = 'identifier_hotkey'
    hotkey = click.prompt('Identifier Hotkey',
                          default=config[k])
    user[k] = hotkey
    print('')

    print('Configuration Completed.')
    print('You can edit your configuration at any time by running:')
    print('$ nx_tools config edit')
    utils.write_json(user, USER_CONFIG_PATH)


@cli.command('edit', short_help="Edit configuration.")
def edit():
    logger = logging.getLogger(__name__)
    filename = USER_CONFIG_PATH
    backup = filename + BACKUP_EXT
    logger.debug('Backing up %s at %s' % (filename, backup))
    shutil.copy(filename, backup)
    editor = NPP
    print('Opening %s with %s.' % (filename, editor))
    subprocess.Popen([editor, filename], shell=True)


@cli.command('revert', short_help='Undo last edit')
def revert():
    logger = logging.getLogger(__name__)
    filename = USER_CONFIG_PATH
    backup = filename + BACKUP_EXT
    logger.debug('Copying %s to %s' % (backup, filename))
    try:
        shutil.copy(backup, filename)
    except IOError as e:
        if e.errno == 2:
            print("Could not find backup file.")
            print("Possible you didn't use 'nx_tools config edit'?")
            return
        else:
            print(e)
            return


@cli.command('list', short_help='List all variables in configuration.')
def list():
    config = utils.read_config()
    print(json.dumps(config, indent=4, separators=(',', ': '), sort_keys=True))
