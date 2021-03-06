"""
Functions for launching NX.

This command uses _list.
"""
import click
import logging
import os
from pprint import pformat
import subprocess

from ..constants import HISTORY_PATH, HISTORY_MAX_RECORDS
from .. import utils
from . import _list


def query(dir_listing, msg):
    print(msg)
    print(_list.pformat_directories(dir_listing))
    chosen_idx = click.prompt(
            '> ', prompt_suffix='',
            type=click.IntRange(min=0, max=len(dir_listing) - 1)
    )
    return dir_listing[chosen_idx]


def set_tmg_var(patch):
    print("Setting UGII_TMG_DIR to: " + patch)
    os.environ["UGII_TMG_DIR"] = patch


def find_ugraf(build_dir, nxbin):
    logger = logging.getLogger(__name__)
    ugii_ugraf = os.path.join(build_dir, 'kits', 'ugii', 'ugraf.exe')
    nxbin_ugraf = os.path.join(build_dir, 'kits', 'nxbin', 'ugraf.exe')
    nxbin_exists = os.path.exists(nxbin_ugraf)
    ugii_exists = os.path.exists(ugii_ugraf)
    if nxbin_exists:
        if nxbin or not ugii_exists:
            return nxbin_ugraf
        else:
            print("WARNING: You won't be able to identify this process."
                  " See issue #16.")
    if not ugii_exists:
        print("Could not find ugraf.exe.\n")
        raise click.Abort

    return ugii_ugraf



def log_entry(PID, nx_version, build_dir, patch_dir, name):
    logger = logging.getLogger(__name__)
    try:
        records = utils.load_json(HISTORY_PATH)
    except IOError:
        records = dict(last_update=0)
    last_update = int(records["last_update"])
    if last_update >= HISTORY_MAX_RECORDS:
        new_update = 1
    else:
        new_update = last_update + 1
    records["last_update"] = new_update
    new_entry = dict(PID=PID,
                     nx_version=nx_version,
                     build=build_dir,
                     patch=patch_dir,
                     name=name)

    logger.debug("New entry for counter %s:\n%s"
                 % (new_update, pformat(new_entry)))
    records[str(new_update)] = new_entry
    utils.write_json(records, HISTORY_PATH)


@click.command('launch', short_help='Launcher.')
@click.argument('nx_version', nargs=1)
@click.option('--latest', is_flag=True,
              help="Launch latest build with latest patch.")
@click.option('--vanilla', is_flag=True,
              help="Use build's internal TMG.")
@click.option('--env-var', is_flag=True,
              help="Use user UGII_TMG_DIR environment variable.")
@click.option('-n', '--name', type=click.STRING,
              help="Name to be associated with process.")
@click.option('--cwd', is_flag=True,
              help="Use current directory as working directory.")
@click.option('--nxbin', is_flag=True,
              help="Launch ugraf.exe from 'nxbin' if possible.")
@click.pass_obj
def cli(config, nx_version, latest, vanilla, env_var, name, cwd, nxbin):
    logger = logging.getLogger(__name__)
    if cwd:
        working_dir = os.getcwd()
    else:
        working_dir = config['start_in']
    logger.debug(utils.pformat_cli_args(locals()))
    build_root, patch_root = utils.get_local_roots(config, nx_version)
    # Get Build
    if utils.is_exe(build_root):
        print("Frozen build.")
        logger.debug("%s is Frozen." % build_root)
        chosen_build = build_root
        ugraf_exe = chosen_build
        if working_dir is None:
            working_dir = 'D:\\'
    else:
        builds_list = _list.list_directories(build_root)
        if latest:
            chosen_build = builds_list[0]
        else:
            chosen_build = query(builds_list, "Pick a build:")
        ugraf_exe = find_ugraf(chosen_build, nxbin)

    # Get Patch and set TMG
    if vanilla:
        chosen_patch = ""
        set_tmg_var("")
    elif env_var:
        chosen_patch = os.environ['UGII_TMG_DIR']
        print("Not setting UGII_TMG_DIR. Currently set to: %s" % chosen_patch)
    else:
        patches_list = _list.list_directories(patch_root)
        if latest:
            chosen_patch = patches_list[0]
        else:
            chosen_patch = query(patches_list, "Pick a patch:")
        tmg_dir = os.path.join(chosen_patch, 'tmg')
        set_tmg_var(tmg_dir)

    if working_dir:
        os.chdir(working_dir)
    cmd = [ugraf_exe]
    logger.debug("Launch command:\n%r" % cmd)
    msg = 'Launching NX from:'
    space = len(msg)
    msg += ' ' + str(ugraf_exe) + '\n'
    msg += '%*s %s' % (space, 'in:', working_dir) if working_dir else ''
    print(msg)
    proc = subprocess.Popen(cmd)
    PID = proc.pid
    log_entry(PID=PID,
              nx_version=nx_version,
              build_dir=os.path.basename(chosen_build),
              patch_dir=os.path.basename(chosen_patch),
              name=name)
