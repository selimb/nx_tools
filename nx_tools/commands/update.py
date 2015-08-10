"""
Functions for updating NX patch and build.
"""
from __future__ import print_function

import click
import ftplib
import glob
import logging
import os
import shutil
import subprocess
import sys

from .. import utils
from .. import exceptions


def get_process_output(process):
    errmsg, _ = process.communicate()
    errmsg = errmsg.decode("utf-8")
    return errmsg


def extract(archive_filepath, exe):
    """Extracts archive file to folder in same directory.

    Args:
      archive_filepath (str): Absolute path to archive file.
      exe (str): Extract command.

    Raises:
      OSError: If the command cannot be run.
    """
    logger = logging.getLogger(__name__)
    output_dir = os.path.join(os.path.dirname(archive_filepath),
                              get_filename(archive_filepath))
    command = [exe, "x", archive_filepath, "-o" + output_dir]
    try:
        print("Extracting...")
        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except WindowsError:
        print("Could not run " + exe)
        raise
    p.wait()
    if p.returncode != 0:
        process_output = get_process_output(process=p)
        print("Could not extract successfully." + process_output)
        # raise WindowsError
        sys.exit()
    logger.debug("File successfully extracted to: " + output_dir)


def get_filename(filepath):
    basename = os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    return filename


def delete_file(filepath):
    print("Deleting file:" + filepath)
    os.remove(filepath)


def is_new(f, target_dir):
    filename = get_filename(f)
    if os.path.isdir(os.path.join(target_dir, filename)):
        return False
    return True


class _Updater(object):

    item_name = None
    item_name_plural = None

    def __init__(self, nx_version, config, source_key):
        self.logger = logging.getLogger(__name__)
        self.nx_version = nx_version.lower()
        try:
            self.remote_dir = config['remote'][source_key][nx_version]
            self.local_dir = config['local'][source_key][nx_version]
        except KeyError:
            print("No configuration found for %s %s."
                  % (nx_version, self.item_name_plural))
            raise exceptions.NXToolsError

        self.zip_exe = config['7z_exe']
        self.new_items = None
        utils.ensure_dir_exists(self.local_dir)

    def _is_new(self, f):
        return is_new(f, self.local_dir)

    def update(self):
        if self.new_items is None:
            self.check()
        if self.new_items == []:
            print("No new %s." % self.item_name)
            return

        number = len(self.new_items)
        if number != 1:
            print("%i new %s found:" % (number, self.item_name_plural))
        else:
            print("One new %s found:" % self.item_name)
        print('\n'.join(map(get_filename, self.new_items)))
        for item in self.new_items:
            dest = os.path.join(self.local_dir, os.path.basename(item))
            self._transfer(item, dest)
            extract(dest, exe=self.zip_exe)
        print("Success!")


def _check(updater, nx_version, config):
    try:
        my_updater = updater(nx_version, config)
    except exceptions.NXToolsError:
        return False
    return my_updater.check()


def _update(updater, nx_version, config):
    try:
        my_updater = updater(nx_version, config)
    except exceptions.NXToolsError:
        return False
    my_updater.update()


class _TMGUpdater(_Updater):
    item_name = 'patch'
    item_name_plural = 'patches'

    def __init__(self, nx_version, config):
        super(_TMGUpdater, self).__init__(nx_version, config, 'patch')
        self._connect()

    def _connect(self):
        # print("Connecting to FTP server...")
        ftp = ftplib.FTP('ftp')
        ftp.login()
        ftp.cwd(self.remote_dir)
        self.ftp = ftp

    def _find_windows_patches(self):
        def is_windows(filename):
            return 'wntx64' in filename or 'win64' in filename
        listings = []
        self.ftp.retrlines("LIST", listings.append)
        found = []
        for listing in listings:
            name = listing.split(None, 8)[-1].lstrip()
            if is_windows(name):
                found.append(name)
        return found

    def _transfer(self, ftp_file, dest_file):
        print("Downloading patch to local directory...")
        self.logger.debug("Patch downloaded to: " + dest_file)
        try:
            with open(dest_file, "wb") as fh:
                self.ftp.retrbinary("RETR " + ftp_file, fh.write)
        except IOError:
            print("FATAL: Check local directory exists.")
            raise

    def check(self):
        self.new_items = []
        self.logger.debug("Checking for %s patch on FTP server..." %
                          self.nx_version.upper())
        windows_patches = self._find_windows_patches()
        if windows_patches == []:
            print("Could not find windows patch.")
            return False

        new_patches = [patch for patch in windows_patches
                       if self._is_new(patch)]
        if new_patches == []:
            self.logger.debug("Not new patch:\n%r" % windows_patches)
            return False

        self.new_items = new_patches
        return True


def check_TMG(nx_version, config):
    return _check(_TMGUpdater, nx_version, config)


def update_TMG(nx_version, config):
    _update(_TMGUpdater, nx_version, config)


class _BuildUpdater(_Updater):
    item_name = 'build'
    item_name_plural = 'builds'
    def __init__(self, nx_version, config):
        super(_BuildUpdater, self).__init__(nx_version, config, 'build')

    def _find_builds(self):
        zips = list(glob.glob(os.path.join(self.remote_dir, "*.7z")))
        return zips

    def _transfer(self, src, dest):
        print("Copying to local directory...")
        self.logger.debug("Copying: {0}\nto: {1}".format(src, dest))
        try:
            shutil.copy(src, dest)
        except IOError as e:
            print('Could not copy\n%s' % e)
            sys.exit(1)

    def check(self):
        self.new_items = []
        self.logger.debug("Checking for %s build in Luc's T drive..."
                          % self.nx_version.upper())
        builds = self._find_builds()
        new_builds = [build for build in builds if self._is_new(build)]
        if new_builds == []:
            self.logger.debug("Not new build:\n%r" % builds)
            return False

        self.new_items = new_builds
        return True


def is_frozen_build(nx_version, config):
    logger = logging.getLogger(__name__)
    if nx_version not in config['remote']['build']:
        logger.debug("No remote found for this version.")
        return True
    if utils.is_exe(config['local']['build'][nx_version]):
        logger.debug("Frozen build: executable")
        return True
    return False


def check_build(nx_version, config):
    return _check(_BuildUpdater, nx_version, config)


def update_build(nx_version, config):
    _update(_BuildUpdater, nx_version, config)


@click.command('check', short_help="Used internally by the Task Scheduler.")
@click.argument('nx_version', nargs=1)
@click.pass_obj
def check_cli(config, nx_version):
    """
    Return Codes:
        200 : Nothing new
        201 : New Build
        202 : New Patch
        203 : Both New Build and New Patch
    """
    new_build = False
    new_patch = False
    if not is_frozen_build(nx_version, config):
        new_build = check_build(nx_version, config)
    new_patch = check_TMG(nx_version, config)
    if new_build and new_patch:
        print("New Build and Patch Available.")
        sys.exit(203)
    if new_build:
        print("New Build Available.")
        sys.exit(201)
    if new_patch:
        print("New Patch Available.")
        sys.exit(202)
    print("Nothing New")
    sys.exit(200)

@click.command('update', short_help='Updater.')
@click.argument('nx_version', nargs=1)
@click.option('--build', is_flag=True,
              help="Only update build.")
@click.option('--patch', is_flag=True,
              help="Only update patch.")
@click.pass_obj
def update_cli(config, nx_version, build, patch):
    logger = logging.getLogger(__name__)
    logger.debug(utils.pformat_cli_args(locals()))
    if not patch and not is_frozen_build(nx_version, config):
        update_build(nx_version, config)
    if not build:
        update_TMG(nx_version, config)
